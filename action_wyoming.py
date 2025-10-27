#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from leds import LedControl
import threading

import os
import re
import queue
import argparse
import asyncio
import logging
import time
from functools import partial
from types import SimpleNamespace
from pprint import pprint

import json
import asyncio

from wyoming.event import Event
from wyoming.satellite import (
    RunSatellite,
    SatelliteConnected,
    SatelliteDisconnected,
    StreamingStarted,
    StreamingStopped,
)
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.vad import VoiceStarted
from wyoming.wake import Detection

CONFIGURATION_ENCODING_FORMAT = "utf-8"

_LOGGER = logging.getLogger()

class LEDsEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        cli_args: argparse.Namespace,
        leds,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.client_id = str(time.monotonic_ns())
        self.leds = leds
        
        self.leds.set_state("idle")    

        _LOGGER.debug("Client connected: %s", self.client_id)

    async def handle_event(self, event: Event) -> bool:
        _LOGGER.debug(event)

        if StreamingStarted.is_type(event.type):
            self.leds.set_state("listening")
        elif VoiceStarted.is_type(event.type):
            self.leds.set_state("speaking")
        #else:
        #    self.leds.set_state("idle")
        return True


# -----------------------------------------------------------------------------


  
async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    _LOGGER.info("Ready")
    
    # Start server
    server = AsyncServer.from_uri(args.uri)
    leds = LedControl()
    try:
        await server.run(partial(LEDsEventHandler, args, leds))
    except KeyboardInterrupt:
        pass
    finally:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass