import os
import csv
import traceback
import argparse
from urllib import urlretrieve, urlopen, quote

BUG_LIST_CSV_URL = """https://bugzilla.redhat.com/buglist.cgi?bug_status={}&classification=Fedora
                    &keywords=Security%2C%20&keywords_type=anywords&longdesc={}&longdesc_type=anywords
                    &product=Fedora&query_format=advanced&resolution=CURRENTRELEASE&resolution=RAWHIDE
                    &resolution=WONTFIX&resolution=CANTFIX&resolution=ERRATA&resolution=NEXTRELEASE
                    &version={}&ctype=csv&human=1"""
BUG_XML_URL = "https://bugzilla.redhat.com/show_bug.cgi?ctype=xml&id={}"

BUGLIST_DIR = "./buglist"
BUGS_DIR = "./bugs"


def get_buglist_file_name(version, bug_status):
    """
    Gives the formatted name of the file containing the buglist info from bugzilla.
    param version: version of the Fedora product.
    param bug_status: One of NEW, ASSIGNED, ON_DEV, POST, MODIFIED, ON_QA, VERIFIED, RELEASE_PENDING, CLOSED.
                    Defaults to CLOSED.
    """
    fname =  str(version) + '_' + bug_status + '.csv'
    return os.path.join(BUGLIST_DIR, fname)


def get_bug_list_csv(long_desc, version, bug_status='CLOSED'):
    """
    Retrieves the list of bugs with Id and some other basic info only if not already pulled.
    param long_desc: The comments to look for in the bug body.
    param version: version of the Fedora product.
    param bug_status: One of NEW, ASSIGNED, ON_DEV, POST, MODIFIED, ON_QA, VERIFIED, RELEASE_PENDING, CLOSED.
                    Defaults to CLOSED.
    """
    
    # Make the buglist directory, only once.
    if not os.path.exists(BUGLIST_DIR):
        os.makedirs(BUGLIST_DIR)
    
    # Concoct the file name to be saved as.
    file_name = get_buglist_file_name(version, bug_status)
    
    # Check if we have brought it already. If so, don't bother.
    if os.path.isfile(file_name):
        return
    
    long_desc_encoded = quote(long_desc)
    url = BUG_LIST_CSV_URL.format(bug_status, long_desc_encoded, version)
    print 'Retriving bug list: version: {}, status: {}'.format(version, bug_status)
    
    try:
        urlretrieve(url, file_name)
    except Exception as e:
        print 'Error retrieving bug list: ' + repr(e)
        traceback.print_exc()
        
    return


def get_bugs(long_desc, version, bug_status='CLOSED'):
    """
    Pulls the buglist if already not pulled, then pulls the individual bugs themselves.
    param long_desc: The comments to look for in the bug body.
    param version: version of the Fedora product.
    param bug_status: One of NEW, ASSIGNED, ON_DEV, POST, MODIFIED, ON_QA, VERIFIED, RELEASE_PENDING, CLOSED.
                    Defaults to CLOSED.
    """
    # Retrieve the bug list if not already gotten.
    get_bug_list_csv(long_desc, version, bug_status)
    
    # Check if we got the bug list properly.
    file_name = get_buglist_file_name(version, bug_status)
    if not os.path.isfile(file_name):
        print 'Oops, something is not right here'
        return
    
    print 'Retriving bug details: version: {}, status: {}'.format(version, bug_status)

    # Open the file and start processing.
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        # Skip the header.
        reader.next()
        for row in reader:
            bug_id = row[0]
            get_bug_detail(bug_id)
            
    return


def get_bug_detail(bug_id, version):
    """
    Retrieves the bug details for a given bug ID. Also puts it in the proper
    version identified folder.
    param bug_id: The unique identifier of the bug.
    param version: The version identified folder for the bug to reside.
    """
    
    # Make the bugs directory, only once.
    bugs_dir = os.path.join(BUGS_DIR, str(version))
    if not os.path.exists(bugs_dir):
        os.makedirs(bugs_dir)

    # FOR NOW - Save it as an xml file, only if the bug file is not already
    # there - ie we have this bug from prior pull for some other run.
    file_name = os.path.join(bugs_dir, str(bug_id) + '.xml')
    if not os.path.isfile(file_name):
        # Get the proper bug xml url from the ID.
        bug_url = BUG_XML_URL.format(bug_id)
        
        # Retrieve the xml for this bug.
        try:
            xml_str = urlopen(bug_url).read()
        except Exception as e:
            print 'Error retrieving bug: {} '.format(bug_id) + repr(e)
            traceback.print_exc()
            
        with open(file_name, 'w') as f:
            f.write(xml_str)
    
    return


def main():
    """
    Point of entry for the script
    """
    ap = argparse.ArgumentParser(description='Use the script to pull Fedora bugzilla issues.')
    ap.add_argument('-d', '-desc', help='Long description of the bug, comma seperated, matches any', required=True)
    ap.add_argument('-v', '-version', help='Fedora product version')
    ap.add_argument('-s', '-bugstatus', help='Status of the bug', 
                    choices=['NEW', 'ASSIGNED', 'ON_DEV', 'POST', 'MODIFIED', 'ON_QA', 'VERIFIED', 'RELEASE_PENDING', 'CLOSED'],
                    default='CLOSED')
    
    args = ap.parse_args()
    
    # Unpack the arguments
    long_desc, version, bug_status = args.d, args.v, args.s
    
    get_bugs(long_desc, version, bug_status)
    return


if __name__ == '__main__':
    main()
