#!/bin/bash

curl -H "Content-Type: application/json" -X POST -d '{"name":["アナと雪","スター・ウォ"]}' http://localhost:8000/api/japan_box