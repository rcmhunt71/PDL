"""
 Basic non-class-based routines specific to the application.
"""

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
from PDL.logger.logger import Logger
from PDL.reporting.invstats import InvStats
from PDL.reporting.summary import ReportingSummary


import pyperclip

LOG = Logger()

"""

The purpose of this module is to define application specific logic, such as processing
input (specific application requirements), URL sanitization, removing duplicates, and
making sure the inventory is up to date.

"""


class NoURLsProvided(Exception):
    """
    General Exception for "No URL was provided" - More descriptive name.
    """


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
    LOG.info("Press CTRL-C to stop buffer scanning.")
    while True:
        try:
            # Read buffer
            buffer = pyperclip.paste().strip()

            # If URL and buffer does not match previous iteration...
            if is_url(buffer) and buffer != last_url:

                # If the URL is already in the buffer, don't duplicate it.
                if buffer in url_list:
                    LOG.info(f"The specified URL is already in the list ({buffer}).")
                    last_url = buffer
                    continue

                # Append the URL in the list and store the link in the last_buffer
                url_list.append(buffer.strip())
                last_url = buffer
                LOG.info(f"({len(url_list)}) Copied '{buffer}'")

            # Give user time to collect another url
            time.sleep(read_delay)

        except KeyboardInterrupt:
            # Control-C detected, break out of loop. Context manager will close file.
            break

    # Bye Felicia!
    LOG.debug(f"Done. {len(url_list)} URLs copied.")
    return url_list


def process_and_record_urls(cfg_obj: PdlConfig) -> list:
    """
    Take the generated list of URLs, and verify all URLs are correct, no duplicates
    (in the list, or downloaded previously).  The resulting list should be written to
    file for archival purposes.

    :param cfg_obj: (PdlConfig): Contains the inventory structure.

    :return: List of valid URLs

    """
    url_file = UrlFile()

    # Check for URLs on the CLI
    raw_url_list = getattr(cfg_obj.cli_args, args.ArgOptions.URLS)

    # If no URLs are provided, check if URL file was specified
    if not raw_url_list:
        LOG.debug("URL list from CLI is empty.")

        # Check for URL file specified on the CLI
        url_file_name = getattr(
            cfg_obj.cli_args, args.ArgOptions.FILE, None)

        # URL file found, so read and store file contents
        if url_file_name is not None:
            url_file_name = os.path.abspath(url_file_name)
            raw_url_list = url_file.read_file(url_file_name)

        # Otherwise was the --buffer option specified the CLI
        elif getattr(cfg_obj.cli_args, args.ArgOptions.BUFFER, False):
            raw_url_list = read_from_buffer()

        # Otherwise, no sure how to proceed... so raise an exception
        else:
            LOG.info(cfg_obj.cli_args)
            LOG.debug("No URL file was specified on the CLI, nor reading from buffer.")
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
        LOG.debug(f"Updated URL File directory for drive letter: {url_file_dir}")

    # If there were URLs available to DL after validation, create the URL file.
    # TODO: Write test to verify URL file is written if there are URLs and no file if there are not URLS
    if cfg_obj.urls:
        url_file.write_file(urls=cfg_obj.urls, create_dir=True, location=url_file_dir)
    else:
        LOG.info("No URLs for DL, no URL FILE created.")

    return cfg_obj.urls


def remove_duplicate_urls_from_inv(cfg_obj: PdlConfig) -> list:
    """
    Remove any provided URLs that were already in the inventory.

    :param cfg_obj: (PdlCfg) - Contains the inventory data structure.

    :return: List of URLs not in the existing inventory

    """
    # Get list of page URLs in inventory.
    page_urls_in_inv = [getattr(image_obj, ImageData.PAGE_URL) for
                        image_obj in cfg_obj.inventory.inventory.values()]

    # Create a copy a list of the provided URLS
    # Used for statistics generation, source list will be modified.
    orig_urls = set(cfg_obj.urls.copy())

    # Create a list of URLs that are not found in the inventory list
    cfg_obj.urls = [url for url in cfg_obj.urls if url not in page_urls_in_inv]

    # Convert to a set so the difference can be generated (and remove any duplicates).
    new_urls = set(cfg_obj.urls.copy())
    duplicates = orig_urls - new_urls

    # List the number of duplicates and the number of URLs to be DL'd
    LOG.info("Removing URLs from existing inventory: Found {dups} duplicates.".format(
        dups=len(orig_urls)-len(new_urls)))
    LOG.info(f"URLs for downloading: {len(new_urls)}")

    # List the specific duplicate URLs
    for dup in duplicates:
        LOG.info(f"Duplicate: {dup}")

    # Return the list of unique URLs that can be DL'd.
    return cfg_obj.urls


def download_images(cfg_obj: PdlConfig) -> None:
    """
    Download the Display pages for the URLS provided.

    :param cfg_obj: (PdlConfig) - Contains the list of URLs to DL

    :return: None

    """
    # Process the urls and return the final list to download
    url_list = process_and_record_urls(cfg_obj=cfg_obj)

    # Import the specified libraries for processing the URLs,
    # based on the user-specified config file
    # -----------------------------------------------
    # CATALOG - DL/parse the display page
    catalog_class = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.CATALOG_PARSE))

    # CONTACT - DL/Parse the actual Image URL
    contact_class = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

    # Log the list of URLs to DL
    LOG.info(f"URL LIST:\n{ArgProcessing.list_urls(url_list=url_list)}")

    # Get the correct image URL from each catalog Page
    cfg_obj.image_data = list()
    image_errors = list()

    # For each URL specified
    for index, page_url in enumerate(url_list):

        # Create a catalog object, and parse the primary image page for
        # the image URL and metadata.
        catalog = catalog_class(page_url=page_url)
        LOG.info(f"({index + 1}/{len(url_list)}) Retrieving URL: {page_url}")
        catalog.get_image_info()

        # If parsing was successful, store the ImageData object created
        # during the parsing
        if (catalog.image_info.image_url is not None and
                catalog.image_info.image_url.lower().startswith(
                    ArgProcessing.PROTOCOL.lower())):
            cfg_obj.image_data.append(catalog.image_info)

        # ERROR encountered. Store the error for reporting after
        # all URLs have been processed.
        else:
            image_errors.append(catalog.image_info)

    # Get a list of the URLs and the ImageData Objects
    downloaded_image_urls = cfg_obj.inventory.get_list_of_image_urls()
    downloaded_images = cfg_obj.inventory.get_list_of_images()
    LOG.debug(f"Have {len(downloaded_image_urls)} URLs in inventory.")

    # Download each image
    for index, image_data in enumerate(cfg_obj.image_data):
        LOG.info(f"{index + 1:>3}: {image_data.image_url}")

        # Create a ContactPage object for storing metadata, location, and statuses.
        contact = contact_class(image_url=image_data.image_url,
                                dl_dir=cfg_obj.dl_dir, image_info=image_data)

        # If both the URL and image name is unique, DL the image.
        # If the image was DL'd by a different/aliased link, the name will be the same,
        # so it will not DL the image again.
        if (image_data.image_url not in downloaded_image_urls and
                image_data.id not in downloaded_images):
            contact.status = contact.download_image()

        else:
            # Gather information about the image was DL'd
            image_metadata = None
            match_type = None

            # If the download URL is in the inventory...
            if image_data.image_url in downloaded_image_urls:
                image_metadata = image_data.image_url
                match_type = "image URL"

            # If the download image is in the inventory...
            elif image_data.id in downloaded_images:
                image_metadata = image_data.id
                match_type = "image name"

            # Report where the image existence was discovered.
            # Set and record the status.
            LOG.info(f"Found {match_type} that exists in metadata: {image_metadata}")
            contact.status = Status.EXISTS

        LOG.info(f'DL STATUS: {contact.status}')

    cfg_obj.inventory.update_inventory(cfg_obj.image_data)
    cfg_obj.inventory.write()

    # Add error_info to be included in results
    cfg_obj.image_data += image_errors

    # Log Results
    results = ReportingSummary(cfg_obj.image_data)
    results.log_download_status_results_table()
    results.log_detailed_download_results_table()

    # Log image metadata (DEBUG)
    if cfg_obj.cli_args.debug:
        for image_data in cfg_obj.image_data:
            LOG.debug(image_data.image_name)
            LOG.debug(pprint.pformat(image_data.to_dict()))

    # If images were downloaded, create the corresponding JSON file
    if cfg_obj.image_data:
        json_logger.JsonLog(
            image_obj_list=cfg_obj.image_data,
            log_filespec=cfg_obj.json_logfile).write_json()
    else:
        LOG.info("No images DL'd. No JSON file created.")


def display_statistics(cfg_obj: PdlConfig) -> None:
    """
    Display the inventory statistics based on the CLI arguments

    :param cfg_obj: PdlConfigObj with inventory.

    :return: None

    """

    # Stats based on AUTHOR
    if getattr(cfg_obj.cli_args, args.ArgOptions.AUTHOR, False):
        LOG.debug("Getting inventory stats by AUTHOR")

    # Stats based on DIRECTORY
    elif getattr(cfg_obj.cli_args, args.ArgOptions.DIRECTORY, False):
        LOG.debug("Getting inventory stats by DIRECTORY")

    # SUMMARY (or no options provided for the STATS submenu)
    else:
        LOG.debug("Getting inventory SUMMARY stats")
        stats = InvStats(cfg_obj.inventory)
        ReportingSummary.log_table(table=stats.inventory_summary_table(), log_level='info')
        data = stats.tally_directory_data("E:\\Other Backups\\System\\Media\\Music\\TC\\500px")
        import pprint
        pprint.pprint(data)
