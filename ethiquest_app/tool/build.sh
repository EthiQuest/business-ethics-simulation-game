#!/bin/bash

# Clean previous build files
flutter pub run build_runner clean

# Generate new files with build_runner
flutter pub run build_runner build --delete-conflicting-outputs