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


def main():
    """
    Primary start up logic.

    :return: None

    """
    app_config = PdlConfig()
    log = AppLogging.configure_logging(app_cfg_obj=app_config)

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
        log.debug("Selected args.ArgSubmodules.DATABASE")

    # -----------------------------------------------------------------
    #                      IMAGE INFO
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.INFO:
        log.debug("Selected args.ArgSubmodules.INFO")
        image = getattr(app_config.cli_args, args.ArgOptions.IMAGE, None).lower()
        if image.lower().endswith('jpg'):
            image = image.split('.')[0]
        if image.lower() in app_config.inventory.inventory.keys():
            log.info(app_config.inventory.inventory[image])
        else:
            log.info(f"Image '{image}' not found.")

    # -----------------------------------------------------------------
    #                UNRECOGNIZED SUB-COMMAND
    # -----------------------------------------------------------------
    else:
        # Should never get here, argparse should prevent it...
        raise args.UnrecognizedModule(app_config.cli_args.command)

    log.info(f"LOGGED TO: {app_config.logfile_name}")


if __name__ == '__main__':
    main()
