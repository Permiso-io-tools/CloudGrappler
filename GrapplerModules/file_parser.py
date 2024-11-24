from GrapplerModules.intel import *


def file_parser(result, cloud_arg1, cloud_arg2,json_output, source_type, intel):
      def remove_line_from_stdout(result, pattern):
   
         filtered_lines = (line for line in result.split('\n') if not line.startswith(pattern) and not line.endswith('...'))
         modified_output_stdout = '\n'.join(filtered_lines)
         return modified_output_stdout


      modified_output_stdout = remove_line_from_stdout(result, 'Searching')

      output_without_bad_character = modified_output_stdout.split('{"key_name":')
      formatted_output = output_without_bad_character[0].strip()
      for index, entry in enumerate(output_without_bad_character[1:]):
         formatted_output += ', ' if index > 0 else '' 
         formatted_output += '{"key_name":' + entry

      formatted_output = "[" + formatted_output + "]"

      process_data(formatted_output,cloud_arg1, cloud_arg2,json_output, source_type, intel)
