# coding=utf-8
from __future__ import absolute_import

import copy
import octoprint.plugin
from octoprint.events import Events
from octoprint_Spoolman.thirdparty.gcodeInterpreter import gcode

class PrinterHandler(octoprint.plugin.BlueprintPlugin):
    def initialize(self):
        self.lastPrintCancelled = False
        self.lastPrintOdometer = None
        self.lastPrintOdometerLoad = None

    def handlePrintingStatusChange(self, eventType):
        if eventType == Events.PRINT_STARTED:
            self.lastPrintCancelled = False
            self.lastPrintOdometer = gcode()
            self.lastPrintOdometerLoad = self.lastPrintOdometer._load(None)

            next(self.lastPrintOdometerLoad)

        if eventType == Events.PRINT_CANCELLED:
            self.lastPrintCancelled = True

        if eventType == Events.PRINT_FAILED and self.lastPrintCancelled:
            # Ignore event, already handled while handling PRINT_CANCELLED
            return

        if (
            eventType == Events.PRINT_PAUSED or
            eventType == Events.PRINT_DONE or
            eventType == Events.PRINT_FAILED or
            eventType == Events.PRINT_CANCELLED
        ):
            self.commitSpoolUsage()

        if (
            eventType == Events.PRINT_DONE or
            eventType == Events.PRINT_FAILED or
            eventType == Events.PRINT_CANCELLED
        ):
            self.lastPrintOdometer = None
            self.lastPrintOdometerLoad = None

    def handlePrintingGCode(self, command):
        if self.lastPrintOdometerLoad == None:
            return

        peek_stats_helpers = self.lastPrintOdometerLoad.send(command)

    def commitSpoolUsage(self):
        peek_stats_helpers = self.lastPrintOdometerLoad.send(False)

        current_extrusion_stats = copy.deepcopy(peek_stats_helpers['get_current_extrusion_stats']())

        peek_stats_helpers['reset_extrusion_stats']()

        self._logger.info("Result: %s", current_extrusion_stats['extrusionAmount'])

        # TODO: get selected spool
        # TODO: get usage amount