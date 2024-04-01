import re


def get_substring_between_delimiters(full_string, start_delimiter, end_delimiter):
    # Define the regex pattern to match content between delimiters
    pattern = rf"{start_delimiter}(.*?){end_delimiter}"

    # Use re.findall to extract content inside delimiters
    extracted_content = re.findall(pattern, full_string, re.DOTALL)
    extracted_content = "".join(extracted_content)
    return extracted_content
