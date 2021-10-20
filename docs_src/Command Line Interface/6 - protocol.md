# Protocol

**Warning: `beep protocol` is still being migrated from a previous codebase; may be unstable.**


`beep protocol` protocol programmatically generates files for running battery experiments. 

The input to `beep protocol` is a singe csv file with various parameters specified, for example:



```csv
project_name,seq_num,template,charge_constant_current_1,charge_percent_limit_1,charge_constant_current_2,charge_cutoff_voltage,charge_constant_voltage_time,charge_rest_time,discharge_profile,profile_charge_limit,max_profile_power,n_repeats,discharge_cutoff_voltage,power_scaling,discharge_rest_time,cell_temperature_nominal,cell_type,capacity_nominal,diagnostic_type,diagnostic_parameter_set,diagnostic_start_cycle,diagnostic_interval
Drive,100,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,4,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,101,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,4,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,102,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,4,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,103,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,4,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,104,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,4,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,105,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,4,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,106,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,8,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,107,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,8,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,108,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,8,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,109,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,8,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,110,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,8,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,111,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,8,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,112,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,12,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,113,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,12,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,114,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,12,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,115,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,12,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,116,diagnosticV5.000,1,30,1,4.1,30,5,US06,4.2,40,12,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,117,diagnosticV5.000,1,30,1,4.1,30,5,LA4,4.2,40,12,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,118,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,4,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,119,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,4,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,120,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,4,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,121,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,4,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,122,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,4,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,123,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,4,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,124,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,8,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,125,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,8,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,126,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,8,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,127,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,8,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,128,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,8,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,129,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,8,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,130,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,12,2.7,0.60,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,131,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,12,2.7,0.27,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,132,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,12,2.7,0.80,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,133,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,12,2.7,0.36,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,134,diagnosticV5.000,1,30,1,3.9,30,5,US06,4.2,40,12,2.7,1.00,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
Drive,135,diagnosticV5.000,1,30,1,3.9,30,5,LA4,4.2,40,12,2.7,0.45,15,25,Tesla_Model3_21700,4.84,HPPC+RPT,Tesla21700,30,200
```

The output of `beep protocol` is a set of ready-to-use battery cycler protocols.


**More documentation for `beep protocol` coming soon.**

![cli_protocol](../static/op_graphic_protocol.png)




## Protocol help dialog

```shell
$: beep protocol --help

Usage: beep protocol [OPTIONS] CSV_FILE

  Generate protocol for battery cyclers from a csv file input.

Options:
  -d, --output-dir TEXT  Directory to output files to. At least three subdirs
                         will be created in this directoryin order to organize
                         the generated protocol files.
  --help                 Show this message and exit.

```



## More documentation coming soon!