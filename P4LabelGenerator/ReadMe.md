# Perforce Memphis Label Generator
 - Use to create Core and Plugin Perforce labels

## Requirements:
  1. [Python](https://www.python.org/downloads/)
  2. Perforce API
     ```
     pip3 install p4python
     ```
  3. Perforce Client needs to be installed
  
## Input:
  1. `PluginName`      - Name of the plugin. (Note: Use `Core` for MemphisCore)
  2. `LabelName`       - Name of the label to be created
  3. `SENLabel`        - Associated SEN Label
  4. `CoreLabel`       - Memphis Core Label (Note: Only required while creating Plugin Label)   

## Usage
- To Create Plugin Label
     ```bash
     python .\P4LabelGenerator.py Concur Concur_ODBC_1.1.1.1000 SimbaEngine_1.1.1.1000 Memphis_Core_ODBC_1.0.0.1000
     ```
- To Create Core Label
     ```bash
     python .\P4LabelGenerator.py Core Memphis_Core_ODBC_1.0.0.1000 SimbaEngine_1.1.1.1000
     ```
  