#!/bin/sh
# Remove any Co-authored-by lines mentioning copilot or bot, and strip Copilot trailers
sed '/Co-authored-by:/I{ /copilot/Id; /bot/Id; }'
