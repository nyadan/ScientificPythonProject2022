# Summarizes the contents of a JSON or CSV file
# author: Nyakas Déniel

import csv
import json
import sys
import re
import numpy as np

# The regular expression used to decide if a field value is a number
number_regex = re.compile(r'(\+|-)?([0-9]+\.?[0-9]*|\.[0-9]+)([eE](\+|-)?[0-9]+)?$')

# Assumed tabular format extension and separator character
tabular_format_and_separators = {'.csv': ',', '.txt': '\t'}

#  Assumed json extension
JSON_format = '.json'

# Intialize a dict to save metadata gathered
metadata = dict()

# Variables for tabular and json
JSON = 'json'
TABULAR = 'tabular'


def get_parameters(parameter_file):
    """ Load content from parameter file into a dict
    Args:
        parameter_file: The parameter file.
    Returns:
         A dict containing the parameters.
    """
    with open(parameter_file) as pf:
        params = json.load(pf)
    return params


def write_to_json(metadata, metafile):
    """ Write the metadata to json metafile.
    Args:
        metadata: The metadata cit.
        metafile: The metafile.
    """
    with open(metafile, 'w') as fp:
        json.dump(metadata, fp, indent=4)


def num_of_rows(infile):
    """ Compute the number of rows.
    Args:
        file: Infile file.
    Returns:
        The number of rows.
    """
    numrows = 0

    if metadata['format'] == JSON:
        with open(infile, 'r') as fp:
            numrows = len(json.load(fp))  # Use len() function to get length of dict
    elif metadata['format'] == TABULAR:
        with open(infile, 'r') as fp:
            inf = csv.reader(fp)
            if metadata['header'] == 1:
                next(inf)  # If it has header, skip it
            for row in inf:
                numrows += 1

    return numrows


def get_format_separator(params):
    """ Get the infile format file format and separator.
    Args:
        params: The parameter dict.
    Returns:
        The infile format and separator.
    """
    infile_format = None
    infile_separator = None

    # Check if info about format is supplied
    if params.__contains__('format') and params.__contains__('separator'):
        infile_format = params['format']
        infile_separator = params['separator']

    else:
        # infer the format of the file from the file extension
        for fmt in tabular_format_and_separators:
            if params['infile'].endswith(fmt):
                infile_format = 'tabular'
                infile_separator = tabular_format_and_separators[fmt]

            elif params['infile'].endswith(JSON_format):
                infile_format = 'json'

    return infile_format, infile_separator


def has_header_row(params):
    """ Check if infile has header row.
    Args:
        params: The parameter dict.
    Returns:
        1 if infile has header, else 0. Returns None if JSON
    """
    header_flag = None

    # Don't bother checking for header if infile is JSON
    if metadata['format'] != JSON:
        if params.__contains__('hasheader'):
            header_flag = params['hasheader']
        else:
            with open(params['infile']) as inf:
                # Return True if the first row appears to be a series of column headers.
                has_header = csv.Sniffer().has_header(inf.read(1024))
                header_flag = 1 if has_header else 0

    return header_flag


def summarize_numeric(st, param_list = []):
    """  Summarize a set of numbers.
    Args:
        st: The set to summarize.
    Returns:
        The the min, max, and mean value in the set.
    """
    ret = dict()
    st = list(st)
    if "max" in param_list:
        ret['max'] = max(st)
    if "min" in param_list:
        ret['min'] = min(st)
    if "mean" in param_list:
        ret['mean'] = float(sum(st)) / len(st)
    if "variance" in param_list:
        ret['variance'] = np.var(st)
    if "range" in param_list:
        ret['range'] = max(st) - min(st)
    if "median" in param_list:
        ret['median'] = np.median(st)
    if "std" in param_list:
        ret['std'] = np.std(st)




    if len(param_list) ==0:
        ret['max'] = max(st)
        ret['min'] = min(st)
        ret['mean'] = float(sum(st)) / len(st)
        ret['variance'] = np.var(st)
        ret['range'] = max(st) - min(st)
        ret['median'] = np.median(st)
        ret['std'] = np.std(st)

    return ret

def summarize_string(st):
    """ Summarize a set of strings.
    Args:
        st: The set of strings
    Returns:
        Number of unique values.
    """
    ret = dict()

    ret['uniquevals'] = len(st)

    return ret


def summarize_set(st, param_list = []):
    """ Summarize field values.
    Args:
        st: The set to summarize.
    Returns:
        The summary of the set
    """

    if all(number_regex.match(str(s)) for s in st):  # If all item in the set are numbers
        ret = summarize_numeric(st, param_list)
        ret.update({'Type': 'numeric'})
    else:
        ret = summarize_string(st)
        ret.update({'Type': 'string'})
    return ret


def convert_fields(iterable, **convertions):
    """ Convert fields.
    Args:
        iterator: The iterator.
        **convertions: Conversion dict.
    Returns:
        The converted value.
    """
    for item in iterable:
        for key in item.keys() & convertions:
            item[key] = convertions[key](item[key])
        yield item


def summarize_list_of_dicts(params, param_list = []):
    """ Compute number of fields, and metadata about the fields.
    Args:
        params: The parameter dict.
    Returns:
        The number of fields, and metadata about the fields
    """

    fields = []
    lst = []
    field_set = set()

    if metadata['format'] == JSON:
        with open(params['infile'], 'r') as jsonfile:
            lst = json.load(jsonfile)
            # Scan the whole file to be sure of finding every variable
            for e in lst:
                for k in e.keys():
                    field_set.add(k)

    elif metadata['format'] == TABULAR:
        with open(params['infile'], 'r') as csvfile:
            mylst = csv.DictReader(csvfile)
            # Use csvreader.fieldnames to receieve fieldsnames if present
            # else use use var1, var2, etc
            mylst.fieldnames = mylst.fieldnames if metadata['header'] else ['var' + str(i) for i in
                                                                            range(1, len(next(mylst)) + 1)]
            field_set = mylst.fieldnames

            # Since csv.DictReader() by default pulls values in columns as strings,
            # I create a generator function that maps the row so their respective data type
            # so I am able to perform computation on them
            fieldconv = {'Milage': float, 'Price': float, 'var4': float, 'var5': float}
            mylst = convert_fields(mylst, **fieldconv)

            for row in mylst:
                lst.append(row)

    for f in field_set:
        ret = dict()
        ret['Name'] = f
        subset = set(e[f] for e in lst)  # Subset containing unique field values to summarize
        ret.update(summarize_set(subset, param_list ))
        fields.append(ret)

    return len(field_set), fields


def run_analysis(file_datas,param_list = []):
    params = file_datas

    # Retrieve infile and metafile, fails and exit if one or both are missing
    try:
        infile = params['infile']
        metafile = params['metafile']
    except KeyError as e:
        print ("Missing parameter definition for '{0}'.".format(e.message))
        sys.exit(1)

    # Collect metadata 'infile'
    metadata['infile'] = infile

    # Collect metadata 'format' and 'separator'
    metadata['format'], metadata['separator'] = get_format_separator(params)

    # Collect metadata 'header'
    metadata['header'] = has_header_row(params)

    # Collect metadata 'numrows'
    metadata['numrows'] = num_of_rows(infile)

    # Collect metadata 'numfields' and 'fields'
    metadata['numfields'], metadata['fields'] = summarize_list_of_dicts(params, param_list)

    # Write metadata to json file
    write_to_json(metadata, metafile)
    print("The file is ready!")