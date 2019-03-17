#!/usr/bin/env python

"""
      PRIMARY APP STARTING POINT.
      --------------
      main() was added to prevent pylint from complaining that variables
      not defined a class/def context should be CONSTANTS.

"""

from PDL.app.pdl_config import PdlConfig, AppLogging
import PDL.app.app as app
import PDL.configuration.cli.args as args
from PDL.engine.inventory.inventory_composite import Inventory
from PDL.logger.utils import num_file_of_type


def determine_number_to_catalog(app_cfg, logger, file_extension='jpg'):
    dl_inventory_count = num_file_of_type(
        directory=app_cfg.dl_dir, file_type=file_extension)
    logger.info(f"Number of files in {app_cfg.dl_dir}:"
                f" {dl_inventory_count}")


def main():
    """
    Primary start up logic.

    :return: None

    """

    app_config = PdlConfig()
    log = AppLogging.configure_logging(app_cfg_obj=app_config)

    def _option_to_be_implemented(module_name):
        log.depth += 1
        log.debug(f"Selected args.ArgSubmodules.{module_name}")
        log.warn(f"'{module_name}' option still to be implemented.")
        log.depth -= 1

    app_config.inventory = Inventory(
        cfg=app_config, force_scan=getattr(app_config.cli_args, args.ArgOptions.FORCE_SCAN))

    # -----------------------------------------------------------------
    #                      DOWNLOAD
    # -----------------------------------------------------------------
    if app_config.cli_args.command == args.ArgSubmodules.DOWNLOAD:
        log.debug("Selected args.ArgSubmodules.DOWNLOAD")
        app.download_images(cfg_obj=app_config)

    # -----------------------------------------------------------------
    #                DUPLICATE MANAGEMENT
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.DUPLICATES:
        log.debug("Selected args.ArgSubmodules.DUPLICATES")
        app_config.inventory.fs_inventory_obj.list_duplicates()
        log.info(app_config.inventory.fs_inventory_obj.list_inventory())

    # -----------------------------------------------------------------
    #                      DATABASE
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.DATABASE:
        _option_to_be_implemented('DATABASE')

    # -----------------------------------------------------------------
    #                      IMAGE INFO
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.INFO:
        log.debug("Selected args.ArgSubmodules.INFO")
        image_id = getattr(app_config.cli_args, args.ArgOptions.IMAGE, None).lower()
        if image_id.lower().endswith('jpg'):
            image_id = image_id.split('.')[0]
        if image_id.lower() in app_config.inventory.inventory.keys():
            log.info(app_config.inventory.inventory[image_id])
        else:
            log.info(f"Image '{image_id}' not found.")

    # -----------------------------------------------------------------
    #                      INVENTORY STATS
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.STATS:
        _option_to_be_implemented('STATS')

    # -----------------------------------------------------------------
    #                UNRECOGNIZED SUB-COMMAND
    # -----------------------------------------------------------------
    else:
        # Should never get here, argparse should prevent it...
        raise args.UnrecognizedModule(app_config.cli_args.command)

    determine_number_to_catalog(app_cfg=app_config, logger=log)
    log.info(f"LOGGED TO: {app_config.logfile_name}")


if __name__ == '__main__':
    main()
