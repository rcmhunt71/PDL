import os
import pprint
import time

from PDL.app.pdl_config import PdlConfig
import PDL.configuration.cli.args as args
from PDL.configuration.cli.url_file import UrlFile
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.properties.app_cfg import (
    AppCfgFileSections, AppCfgFileSectionKeys)
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus as Status
from PDL.engine.module_imports import import_module_class
import PDL.logger.json_log as json_logger
from PDL.logger.logger import Logger as Logger
from PDL.reporting.summary import ReportingSummary

import pyperclip

log = Logger()


class NoURLsProvided(Exception):
    pass


def is_url(target_string: str) -> bool:
    """
    Verify target_string is a URL
    :param target_string: String to test
    :return: (Boolean) Is a URL? T/F
    """
    return target_string.lstrip().lower().startswith('http')


def read_from_buffer(read_delay: float = 0.25) -> list:
    """
    Read URLs from OS copy/paste buffer.
    :param read_delay: Amount of time between each polling of the buffer.
    :return: list of URLs

    """
    last_url = None
    url_list = list()
    log.info("Press CTRL-C to stop buffer scanning.")
    while True:
        try:
            # Read buffer
            buffer = pyperclip.paste().strip()

            # If URL and buffer does not match previous iteration...
            if is_url(buffer) and buffer != last_url:

                # If the URL is already in the buffer, don't duplicate it.
                if buffer in url_list:
                    log.info(f"The specified URL is already in the list ({buffer}).")
                    last_url = buffer
                    continue

                # Append the URL in the list and store the link in the last_buffer
                url_list.append(buffer.strip())
                last_url = buffer
                log.info(f"({len(url_list)}) Copied '{buffer}'")

            # Give user time to collect another url
            time.sleep(read_delay)

        except KeyboardInterrupt:
            # Control-C detected, break out of loop. Context manager will close file.
            break

    # Bye Felicia!
    log.debug(f"Done. {len(url_list)} URLs copied.")
    return url_list


def process_and_record_urls(cfg_obj: PdlConfig) -> list:
    url_file = UrlFile()

    # Check for URLs on the CLI
    raw_url_list = getattr(cfg_obj.cli_args, args.ArgOptions.URLS)

    # If no URLs are provided, check if URL file was specified
    if not raw_url_list:
        log.debug("URL list from CLI is empty.")

        # Check for URL file
        url_file_name = getattr(
            cfg_obj.cli_args, args.ArgOptions.FILE, None)

        if url_file_name is not None:
            url_file_name = os.path.abspath(url_file_name)
            raw_url_list = url_file.read_file(url_file_name)

        elif getattr(cfg_obj.cli_args, args.ArgOptions.BUFFER, False):
            raw_url_list = read_from_buffer()

        else:
            log.info(cfg_obj.cli_args)
            log.debug("No URL file was specified on the CLI, nor reading from buffer.")
            raise NoURLsProvided()

    # Determine the supported URL domains (to remove junk/unexpected URLs)
    url_domains = cfg_obj.app_cfg.get_list(
        AppCfgFileSections.PROJECT, AppCfgFileSectionKeys.URL_DOMAINS)

    # Sanitize the URL list (missing spaces, duplicates, valid and accepted URLs)
    cfg_obj.urls = ArgProcessing.process_url_list(raw_url_list, domains=url_domains)

    # Remove duplicates from the inventory (can be disabled via CLI)
    if not cfg_obj.cli_args.ignore_dups:
        cfg_obj.urls = remove_duplicate_urls_from_inv(cfg_obj)

    # Write the file of accepted/sanitized URLs to be processed
    url_file_dir = cfg_obj.app_cfg.get(AppCfgFileSections.LOGGING,
                                       AppCfgFileSectionKeys.URL_FILE_DIR)
    url_file_drive = cfg_obj.app_cfg.get(AppCfgFileSections.LOGGING,
                                         AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
    if url_file_drive is not None:
        url_file_dir = f"{url_file_drive}:{url_file_dir}"
        log.debug(f"Updated URL File directory for drive letter: {url_file_dir}")

    if len(cfg_obj.urls) > 0:
        url_file.write_file(urls=cfg_obj.urls, create_dir=True, location=url_file_dir)
    else:
        log.info("No URLs for DL, no URL FILE created.")
    return cfg_obj.urls


def remove_duplicate_urls_from_inv(cfg_obj: PdlConfig) -> list:
    page_urls_in_inv = [getattr(image_obj, ImageData.PAGE_URL) for
                        image_obj in cfg_obj.inventory.inventory.values()]
    orig_urls = set(cfg_obj.urls.copy())

    cfg_obj.urls = [url for url in cfg_obj.urls if url not in page_urls_in_inv]
    new_urls = set(cfg_obj.urls.copy())
    duplicates = orig_urls - new_urls

    log.info("Removing URLs from existing inventory: Found {dups} duplicates.".format(
        dups=len(orig_urls)-len(new_urls)))
    log.info(f"URLs for downloading: {len(new_urls)}")

    for dup in duplicates:
        log.info(f"Duplicate: {dup}")

    return cfg_obj.urls


def download_images(cfg_obj: PdlConfig) -> None:
    # Process the urls and return the final list to download
    url_list = process_and_record_urls(cfg_obj=cfg_obj)

    # Import the specified libraries for processing the URLs, based on the config file
    catalog_class = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.CATALOG_PARSE))

    contact_class = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

    log.info(f"URL LIST:\n{ArgProcessing.list_urls(url_list=url_list)}")

    # Get the correct image URL from each catalog Page
    cfg_obj.image_data = list()
    image_errors = list()
    for index, page_url in enumerate(url_list):

        # Parse the primary image page for the image URL and metadata.
        catalog = catalog_class(page_url=page_url)
        log.info(f"({index + 1}/{len(url_list)}) Retrieving URL: {page_url}")
        catalog.get_image_info()

        # If parsing was successful, store the image URL
        if (catalog.image_info.image_url is not None and
                catalog.image_info.image_url.lower().startswith(
                    ArgProcessing.PROTOCOL.lower())):
            cfg_obj.image_data.append(catalog.image_info)
        else:
            image_errors.append(catalog.image_info)

    downloaded_image_urls = cfg_obj.inventory.get_list_of_image_urls()
    downloaded_images = cfg_obj.inventory.get_list_of_images()
    log.debug(f"Have {len(downloaded_image_urls)} URLs in inventory.")

    # Download each image
    for index, image_data in enumerate(cfg_obj.image_data):
        log.info(f"{index + 1:>3}: {image_data.image_url}")
        contact = contact_class(image_url=image_data.image_url, dl_dir=cfg_obj.dl_dir, image_info=image_data)
        image_filename = image_data.filename.split('.')[0]
        if image_data.image_url not in downloaded_image_urls and image_filename not in downloaded_images:
            status = contact.download_image()
        else:
            image_metadata = None
            if image_data.image_url in downloaded_image_urls:
                image_metadata = image_data.image_url
            elif image_filename in downloaded_images:
                image_metadata = image_filename
            log.info(f"Found image url that exists in metadata: {image_metadata}")
            status = Status.EXISTS
            contact.status = status
            contact.image_info.dl_status = status
        log.info(f'DL STATUS: {status}')

    # Add error_info to be included in results
    cfg_obj.image_data += image_errors

    # Log Results
    results = ReportingSummary(cfg_obj.image_data)
    results.log_download_status_results_table()
    results.log_detailed_download_results_table()

    # Log image metadata (DEBUG)
    if cfg_obj.cli_args.debug:
        for image_data in cfg_obj.image_data:
            log.debug(image_data.image_name)
            log.debug(pprint.pformat(image_data.to_dict()))

    # If images were downloaded, create the corresponding JSON file
    if cfg_obj.image_data:
        json_logger.JsonLog(
            image_obj_list=cfg_obj.image_data,
            log_filespec=cfg_obj.json_logfile).write_json()
    else:
        log.info("No images DL'd. No JSON file created.")