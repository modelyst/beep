# Copyright 2019 Toyota Research Institute. All rights reserved.
"""Unit tests related to Generating protocol files"""

import os
import unittest
import warnings
import json
import boto3
import numpy as np
import datetime

import pandas as pd
from beep import ENVIRONMENT
from beep.protocol import PROCEDURE_TEMPLATE_DIR, SCHEDULE_TEMPLATE_DIR
from beep.generate_protocol import Procedure, \
    generate_protocol_files_from_csv, convert_velocity_to_power_waveform, generate_maccor_waveform_file
from beep.protocol.arbin import Schedule
from beep.protocol.maccor_to_arbin import ProcedureToSchedule
from monty.tempfile import ScratchDir
from monty.serialization import dumpfn, loadfn
from monty.os import makedirs_p
from botocore.exceptions import NoRegionError, NoCredentialsError
from beep.utils import os_format, hash_file

import difflib
from beep.utils.secrets_manager import secret_accessible

TEST_DIR = os.path.dirname(__file__)
TEST_FILE_DIR = os.path.join(TEST_DIR, "test_files")


def event_setup():
    # Setup events for testing
    if not secret_accessible(ENVIRONMENT):
        events_mode = "events_off"
    else:
        try:
            kinesis = boto3.client('kinesis')
            response = kinesis.list_streams()
            events_mode = "test"
        except Exception as e:
            warnings.warn("Cloud resources not configured")
            events_mode = "events_off"
    return events_mode
  
class ProcedureTest(unittest.TestCase):
    def setUp(self):
        self.events_mode = event_setup()
        # Determine events mode for testing
        
    def test_convert_velocity_to_power_waveform(self):
        velocity_waveform_file = os.path.join(TEST_FILE_DIR, "LA4_velocity_waveform.txt")
        df_velocity = pd.read_csv(velocity_waveform_file, sep="\t", header=0)
        df_power = convert_velocity_to_power_waveform(velocity_waveform_file, 'mph')
        #Check input and output sizes
        self.assertEqual(len(df_velocity), len(df_power))
        self.assertTrue(any(df_power['power']<0))

    def test_generate_maccor_waveform_file_default(self):
        velocity_waveform_file = os.path.join(TEST_FILE_DIR, "LA4_velocity_waveform.txt")
        with ScratchDir('.') as scratch_dir:

            df_power = convert_velocity_to_power_waveform(velocity_waveform_file, 'mph')
            df_MWF = pd.read_csv(generate_maccor_waveform_file(df_power, "test_LA4_waveform", scratch_dir), sep='\t', header=None)

            #Reference mwf file generated by the cycler for the same power waveform.
            df_MWF_ref = pd.read_csv(os.path.join(TEST_FILE_DIR, "LA4_reference_default_settings.mwf"), sep="\t", header=None)

            self.assertEqual(df_MWF.shape, df_MWF_ref.shape)

            #Check that the fourth column for charge/discharge limit is empty (default setting)
            self.assertTrue(df_MWF.iloc[:,3].isnull().all())

            #Check that sum of durations equals length of the power timeseries
            self.assertEqual(df_MWF.iloc[:,5].sum(), len(df_power))

            #Check that charge/discharge steps are identical
            self.assertTrue((df_MWF.iloc[:,0] == df_MWF_ref.iloc[:,0]).all())

            #Check that power values are close to each other (col 2)
            relative_differences = np.abs((df_MWF.iloc[:,2] - df_MWF_ref.iloc[:,2]) / df_MWF_ref.iloc[:,2])
            self.assertLessEqual(np.mean(relative_differences)*100, 0.01) #mean percentage error < 0.01%

    def test_generate_maccor_waveform_file_custom(self):
        velocity_waveform_file = os.path.join(TEST_FILE_DIR, "US06_velocity_waveform.txt")
        mwf_config = {'control_mode': 'I',
                      'value_scale': 1,
                      'charge_limit_mode': 'R',
                      'charge_limit_value': 2,
                      'discharge_limit_mode': 'P',
                      'discharge_limit_value': 3,
                      'charge_end_mode': 'V',
                      'charge_end_operation': '>=',
                      'charge_end_mode_value': 4.2,
                      'discharge_end_mode': 'V',
                      'discharge_end_operation': '<=',
                      'discharge_end_mode_value': 3,
                      'report_mode': 'T',
                      'report_value': 10,
                      'range': 'A',
                      }
        with ScratchDir('.') as scratch_dir:
            df_power = convert_velocity_to_power_waveform(velocity_waveform_file, 'mph')
            df_MWF = pd.read_csv(generate_maccor_waveform_file(df_power, "test_US06_waveform", scratch_dir,
                                                               mwf_config=mwf_config), sep='\t', header=None)
            df_MWF_ref = pd.read_csv(os.path.join(TEST_FILE_DIR, "US06_reference_custom_settings.mwf"), sep="\t", header=None)

            #Check dimensions with the reference mwf file
            self.assertEqual(df_MWF.shape, df_MWF_ref.shape)

            #Check that control_mode, charge/discharge state, limit and limit_value columns are identical.
            self.assertTrue((df_MWF.iloc[:, [0,1,3,4]] == df_MWF_ref.iloc[:, [0,1,3,4]]).all().all())

            #Check that power values are close to each other (col 2)
            relative_differences = np.abs((df_MWF.iloc[:,2] - df_MWF_ref.iloc[:,2]) / df_MWF_ref.iloc[:,2])
            self.assertLessEqual(np.mean(relative_differences)*100, 0.01) #mean percentage error < 0.01%

class GenerateProcedureTest(unittest.TestCase):
    def setUp(self):
        self.events_mode = event_setup()

    def test_io(self):
        test_file = os.path.join(TEST_FILE_DIR, 'xTESLADIAG_000003_CH68.000')
        json_file = os.path.join(TEST_FILE_DIR, 'xTESLADIAG_000003_CH68.json')
        test_out = 'test1.000'

        procedure = Procedure.from_file(os.path.join(TEST_FILE_DIR, test_file))
        with ScratchDir('.'):
            dumpfn(procedure, json_file)
            procedure.to_file(test_out)
            hash1 = hash_file(test_file)
            hash2 = hash_file(test_out)
            if hash1 != hash2:
                original = open(test_file).readlines()
                parsed = open(test_out).readlines()
                self.assertFalse(list(difflib.unified_diff(original, parsed)))
                for line in difflib.unified_diff(original, parsed):
                    self.assertIsNotNone(line)

        test_file = os.path.join(TEST_FILE_DIR, 'xTESLADIAG_000004_CH69.000')
        json_file = os.path.join(TEST_FILE_DIR, 'xTESLADIAG_000004_CH69.json')
        test_out = 'test2.000'

        procedure = Procedure.from_file(os.path.join(TEST_FILE_DIR, test_file))
        with ScratchDir('.'):
            dumpfn(procedure, json_file)
            procedure.to_file(test_out)
            hash1 = hash_file(test_file)
            hash2 = hash_file(test_out)
            if hash1 != hash2:
                original = open(test_file).readlines()
                parsed = open(test_out).readlines()
                self.assertFalse(list(difflib.unified_diff(original, parsed)))
                for line in difflib.unified_diff(original, parsed):
                    self.assertIsNotNone(line)

    def test_generate_proc_exp(self):
        test_file = os.path.join(TEST_FILE_DIR, 'EXP.000')
        json_file = os.path.join(TEST_FILE_DIR, 'EXP.json')
        test_out = 'test_EXP.000'
        test_parameters = ["4.2", "2.0C", "2.0C"]
        procedure = Procedure.from_exp(*test_parameters)
        with ScratchDir('.'):
            dumpfn(procedure, json_file)
            procedure.to_file(test_out)
            hash1 = hash_file(test_file)
            hash2 = hash_file(test_out)
            if hash1 != hash2:
                original = open(test_file).readlines()
                parsed = open(test_out).readlines()
                self.assertFalse(list(difflib.unified_diff(original, parsed)))
                for line in difflib.unified_diff(original, parsed):
                    self.assertIsNotNone(line)

    def test_missing(self):
        test_parameters = ["EXP", "4.2", "2.0C", "2.0C"]
        template = os.path.join(TEST_FILE_DIR, "EXP_missing.000")
        self.assertRaises(UnboundLocalError, Procedure.from_exp,
                          *test_parameters[1:]+[template])

    def test_from_csv(self):
        csv_file = os.path.join(TEST_FILE_DIR, "parameter_test.csv")

        # Test basic functionality
        with ScratchDir('.') as scratch_dir:
            makedirs_p(os.path.join(scratch_dir, "procedures"))
            makedirs_p(os.path.join(scratch_dir, "names"))
            generate_protocol_files_from_csv(csv_file, scratch_dir)
            self.assertEqual(len(os.listdir(os.path.join(scratch_dir, "procedures"))), 3)

        # Test avoid overwriting file functionality
        with ScratchDir('.') as scratch_dir:
            makedirs_p(os.path.join(scratch_dir, "procedures"))
            makedirs_p(os.path.join(scratch_dir, "names"))
            dumpfn({"hello": "world"}, os.path.join("procedures", "name_000007.000"))
            generate_protocol_files_from_csv(csv_file, scratch_dir)
            post_file = loadfn(os.path.join("procedures", "name_000007.000"))
            self.assertEqual(post_file, {"hello": "world"})
            self.assertEqual(len(os.listdir(os.path.join(scratch_dir, "procedures"))), 3)

    def test_from_csv_2(self):
        csv_file = os.path.join(TEST_FILE_DIR, "PredictionDiagnostics_parameters.csv")

        # Test basic functionality
        with ScratchDir('.') as scratch_dir:
            makedirs_p(os.path.join(scratch_dir, "procedures"))
            makedirs_p(os.path.join(scratch_dir, "names"))
            generate_protocol_files_from_csv(csv_file, scratch_dir)
            self.assertEqual(len(os.listdir(os.path.join(scratch_dir, "procedures"))), 2)

            original = open(os.path.join(PROCEDURE_TEMPLATE_DIR, "diagnosticV2.000")).readlines()
            parsed = open(os.path.join(os.path.join(scratch_dir, "procedures"),
                                       "PredictionDiagnostics_000000.000")).readlines()
            self.assertFalse(list(difflib.unified_diff(original, parsed)))
            for line in difflib.unified_diff(original, parsed):
                self.assertIsNotNone(line)

            original = open(os.path.join(PROCEDURE_TEMPLATE_DIR, "diagnosticV3.000")).readlines()
            parsed = open(os.path.join(os.path.join(scratch_dir, "procedures"),
                                       "PredictionDiagnostics_000196.000")).readlines()
            diff = list(difflib.unified_diff(original, parsed))
            diff_expected = ['--- \n', '+++ \n', '@@ -27,7 +27,7 @@\n', '           <SpecialType> </SpecialType>\n',
                             '           <Oper> = </Oper>\n', '           <Step>002</Step>\n',
                             '-          <Value>03:00:00</Value>\n',
                             '+          <Value>03:12:00</Value>\n', '         </EndEntry>\n', '         <EndEntry>\n',
                             '           <EndType>Voltage </EndType>\n']
            self.assertEqual(diff, diff_expected)
            for line in difflib.unified_diff(original, parsed):
                self.assertIsNotNone(line)

            _, namefile = os.path.split(csv_file)
            namefile = namefile.split('_')[0] + '_names_'
            namefile = namefile + datetime.datetime.now().strftime("%Y%m%d_%H%M") + '.csv'
            names_test = open(os.path.join(scratch_dir, "names", namefile)).readlines()
            self.assertEqual(names_test, ['PredictionDiagnostics_000000_\n', 'PredictionDiagnostics_000196_\n'])

    @unittest.skip
    def test_from_csv_3(self):

        csv_file_list = os.path.join(TEST_FILE_DIR, "PreDiag_parameters - GP.csv")
        makedirs_p(os.path.join(TEST_FILE_DIR, "procedures"))
        makedirs_p(os.path.join(TEST_FILE_DIR, "names"))
        generate_protocol_files_from_csv(csv_file_list, TEST_FILE_DIR)
        if os.path.isfile(os.path.join(TEST_FILE_DIR, "procedures", ".DS_Store")):
            os.remove(os.path.join(TEST_FILE_DIR, "procedures", ".DS_Store"))
        self.assertEqual(len(os.listdir(os.path.join(TEST_FILE_DIR, "procedures"))), 265)

    def test_console_script(self):
        csv_file = os.path.join(TEST_FILE_DIR, "parameter_test.csv")

        # Test script functionality
        with ScratchDir('.') as scratch_dir:
            # Set BEEP_PROCESSING_DIR directory to scratch_dir
            os.environ['BEEP_PROCESSING_DIR'] = os.getcwd()
            procedures_path = os.path.join("data-share", "protocols", "procedures")
            names_path = os.path.join("data-share", "protocols", "names")
            makedirs_p(procedures_path)
            makedirs_p(names_path)

            # Test the script
            json_input = json.dumps(
                {"file_list": [csv_file],
                 "mode": self.events_mode})
            os.system("generate_protocol {}".format(os_format(json_input)))
            self.assertEqual(len(os.listdir(procedures_path)), 3)

class ProcedureToScheduleTest(unittest.TestCase):

    def setUp(self):
        self.events_mode = event_setup()

    def test_single_step_conversion(self):
        procedure = Procedure()

        templates = PROCEDURE_TEMPLATE_DIR

        test_file = 'diagnosticV3.000'
        json_file = 'test.json'

        proc_dict, sp = procedure.to_dict(os.path.join(templates, test_file),
                                          os.path.join(templates, json_file)
                                          )
        proc_dict = procedure.maccor_format_dict(proc_dict)
        test_step_dict = proc_dict['MaccorTestProcedure']['ProcSteps']['TestStep']

        converter = ProcedureToSchedule(test_step_dict)
        step_index = 5
        step_name_list, step_flow_ctrl = converter.create_metadata()

        self.assertEqual(step_flow_ctrl[7], '5-reset cycle C/20')
        self.assertEqual(step_flow_ctrl[68], '38-reset cycle')

        step_arbin = converter.compile_to_arbin(test_step_dict[step_index], step_index, step_name_list, step_flow_ctrl)
        self.assertEqual(step_arbin['m_szLabel'], '6-None')
        self.assertEqual(step_arbin['[Schedule_Step5_Limit0]']['m_szGotoStep'], 'Next Step')
        self.assertEqual(step_arbin['[Schedule_Step5_Limit0]']['Equation0_szLeft'], 'PV_CHAN_Voltage')
        self.assertEqual(step_arbin['[Schedule_Step5_Limit2]']['m_szGotoStep'], '70-These are the 2 reset cycles')

        step_index = 8
        step_arbin = converter.compile_to_arbin(test_step_dict[step_index], step_index, step_name_list, step_flow_ctrl)
        print(step_index, test_step_dict[step_index])
        print(step_arbin)
        self.assertEqual(step_arbin['[Schedule_Step8_Limit0]']['Equation0_szLeft'], 'PV_CHAN_CV_Stage_Current')
        self.assertEqual(step_arbin['[Schedule_Step8_Limit0]']['Equation0_szRight'],
                         test_step_dict[step_index]['Ends']['EndEntry'][0]['Value'])
        os.remove(os.path.join(templates, json_file))

    def test_serial_conversion(self):
        procedure = Procedure()

        templates = PROCEDURE_TEMPLATE_DIR

        test_file = 'diagnosticV3.000'
        json_file = 'test.json'

        proc_dict, sp = procedure.to_dict(os.path.join(templates, test_file),
                                          os.path.join(templates, json_file)
                                          )
        proc_dict = procedure.maccor_format_dict(proc_dict)
        test_step_dict = proc_dict['MaccorTestProcedure']['ProcSteps']['TestStep']

        converter = ProcedureToSchedule(test_step_dict)
        step_name_list, step_flow_ctrl = converter.create_metadata()

        for step_index, step in enumerate(test_step_dict):
            if 'Loop' in step['StepType']:
                print(step_index, step)
            step_arbin = converter.compile_to_arbin(test_step_dict[step_index], step_index,
                                                    step_name_list, step_flow_ctrl)
            if 'Loop' in step['StepType']:
                self.assertEqual(step_arbin['m_szStepCtrlType'], 'Set Variable(s)')
                self.assertEqual(step_arbin['m_uLimitNum'], '2')
            if step_index == 15:
                self.assertEqual(step_arbin['[Schedule_Step15_Limit0]']['m_szGotoStep'], '11-None')
                self.assertEqual(step_arbin['[Schedule_Step15_Limit1]']['m_szGotoStep'], 'Next Step')
        os.remove(os.path.join(templates, json_file))

    def test_schedule_creation(self):
        procedure = Procedure()

        templates = PROCEDURE_TEMPLATE_DIR

        test_file = 'diagnosticV3.000'
        json_file = 'test.json'
        sdu_test_input = os.path.join(SCHEDULE_TEMPLATE_DIR, '20170630-3_6C_9per_5C.sdu')
        sdu_test_output = os.path.join(TEST_FILE_DIR, 'schedule_test_output.sdu')

        proc_dict, sp = procedure.to_dict(os.path.join(templates, test_file),
                                          os.path.join(templates, json_file)
                                          )
        proc_dict = procedure.maccor_format_dict(proc_dict)
        test_step_dict = proc_dict['MaccorTestProcedure']['ProcSteps']['TestStep']

        converter = ProcedureToSchedule(test_step_dict)
        converter.create_sdu(sdu_test_input, sdu_test_output)
        os.remove(os.path.join(templates, json_file))
        os.remove(sdu_test_output)


class ArbinScheduleTest(unittest.TestCase):
    def setUp(self):
        self.events_mode = event_setup()

    def test_dict_to_file(self):
        filename = '20170630-3_6C_9per_5C.sdu'
        schedule = Schedule.from_file(os.path.join(SCHEDULE_TEMPLATE_DIR, filename))
        testname = 'test1.sdu'
        with ScratchDir('.'):
            dumpfn(schedule, "schedule_test.json")
            schedule.to_file(testname)
            hash1 = hash_file(os.path.join(SCHEDULE_TEMPLATE_DIR, filename))
            hash2 = hash_file(testname)
            if hash1 != hash2:
                original = open(os.path.join(SCHEDULE_TEMPLATE_DIR, filename), encoding='latin-1').read()
                parsed = open(testname, encoding='latin-1').read()
                self.assertFalse(list(difflib.unified_diff(original, parsed)))
                for line in difflib.unified_diff(original, parsed):
                    print(line)

    def test_fastcharge(self):
        filename = '20170630-3_6C_9per_5C.sdu'
        test_file = 'test.sdu'
        sdu = Schedule.from_fast_charge(1.1 * 3.6, 0.086, 1.1 * 5, os.path.join(SCHEDULE_TEMPLATE_DIR, filename))
        with ScratchDir('.'):
            sdu.to_file(test_file)
            hash1 = hash_file(os.path.join(SCHEDULE_TEMPLATE_DIR, filename))
            hash2 = hash_file(test_file)
            if hash1 != hash2:
                original = open(os.path.join(SCHEDULE_TEMPLATE_DIR, filename), encoding='latin-1').readlines()
                parsed = open(test_file, encoding='latin-1').readlines()
                udiff = list(difflib.unified_diff(original, parsed))
                for line in udiff:
                    print(line)
                self.assertFalse(udiff)
