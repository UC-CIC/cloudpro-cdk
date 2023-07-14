#!/bin/bash

tar -a -c -f ./cloudpro_cdk/lambda/custom_packages/layers/cloudpro_lib.zip -C cloudpro_cdk/lambda/custom_packages/src python/pro_parsers python/scoring_safety python/json_encoder