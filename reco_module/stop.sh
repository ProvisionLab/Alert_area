#!/bin/bash

sudo supervisorctl stop reco

ps x | grep reco | cut -f 1 -d ' '
