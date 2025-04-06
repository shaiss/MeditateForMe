#!/bin/bash

# Watch and build Tailwind CSS when changes are detected
npx tailwindcss -i ./static/css/src/main.css -o ./static/css/styles.css --watch
