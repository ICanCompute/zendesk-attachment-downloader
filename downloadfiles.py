import calendar
import os
import time
import urllib
import re


class DownloadFiles(object):
    """Class which downloads and extracts files."""
    extToCommand = {".tar.gz": "tar xzf",
                    ".tgz": "tar xzf",
                    ".tar.bz2": "tar xjf",
                    ".tbz": "tar xjf",
                    ".zip": "unzip",
                    ".gz": "gunzip",
                    ".bz2": "bunzip2",
                    ".7z": "7z x",
                    ".rtf": "textutil -convert txt",
                    ".doc": "textutil -convert txt",
                    ".docx": "textutil -convert txt"}
    extNoCd = {".rtf", ".doc", ".docx"}

    def filename_split(self, filename):
        """
        Return the filename root and extension taking multi-extension files, like .tar.gz, into account

        :param filename: the filename to split
        """
        root, extension = os.path.splitext(filename)
        last_extension = full_extension = extension
        while extension:
            root, extension = os.path.splitext(root)
            full_extension = extension + full_extension
            if full_extension in DownloadFiles.extToCommand:
                last_extension = full_extension

        full_extension = full_extension.lower()
        last_extension = last_extension.lower()
        return root, full_extension, last_extension

    def fix_filename(self, file_id, filename):
        """Make filename ZenDesk organizational friendly"""
        root, full_extension, last_extention = self.filename_split(filename)
        if not full_extension:
            full_extension = '.txt'
        #Clean up name
        root = re.sub(r"[^a-zA-Z_0-9\-]", "", root)
        return '%s_%s%s' % (root, file_id, full_extension)

    def get_formatted_time(self, created_at):
        """Correctly format the time for touch -t from the provided ZenDesk timestamp"""
        time_format = '%Y-%m-%dT%H:%M:%S'
        created_time = created_at[:-1]
        created_stamp = calendar.timegm(time.strptime(created_time, time_format))
        created_date = time.localtime(created_stamp)
        formatted_time = time.strftime('%Y%m%d%H%M', created_date)
        return formatted_time

    def touch_file(self, filetime, filename):
        """
        Modify the created and modified timestamps of the given file

        :param filetime: the time to use
        :param filename: the file to touch
        """
        os.system('touch -t  {0} "{1}"'.format(filetime, filename))
        os.system('touch -mt {0} "{1}"'.format(filetime, filename))

    def maybe_create_dir_and_run_command(self, command, filename, dir_name=''):
        """
        Run the command on the given file.  If a directory is specified, run the command
        inside the given directory.  If needed create the directory first.

        :param command: command to run
        :param filename: file to run it on
        :param dir_name: directory to run it from
        """
        prefix = ""
        if dir_name and not os.path.isdir(dir_name):
            os.makedirs(dir_name)
            prefix = 'cd "{0}";'.format(dir_name)
        os.system(prefix + command + ' "{0}"'.format(filename))

    def check_and_extract_files(self, download_directory, filename, local_filename, formatted_time):
        """
        Extract files to their proper directories if file type is known

        :param download_directory: where to find the file file
        :param filename: full path to file
        :param local_filename: filename only
        :param formatted_time: timestamp of the file
        """
        # Compare known extractable file extensions to see if there is a match
        file_root, file_extension, final_extension = self.filename_split(filename)
        if not file_extension in DownloadFiles.extToCommand:
            if final_extension in DownloadFiles.extToCommand:
                file_extension = final_extension
            else:
                return

        # Calculate and archive directory
        command = DownloadFiles.extToCommand[file_extension]
        archive_folder = os.path.join(download_directory, file_root) if file_extension not in DownloadFiles.extNoCd else ''

        # Perform the actual extraction process
        output = "Using '{0}' to extract '{1}'".format(command, filename)
        if archive_folder:
            output += " into '{0}'".format(archive_folder)
        print output

        self.maybe_create_dir_and_run_command(command, local_filename, archive_folder)

    def download_files(self, base_download_directory, attachment_info):
        """Download all the files provided in the attachments dictionary"""
        # Ensure the download directory exists
        download_directory = os.path.join(base_download_directory, attachment_info['user'], attachment_info['name'])
        #download_directory = os.path.join(base_download_directory, attachment_info['organization_id'], attachment_info['name'])
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        # Download each attachment
        for attachment in attachment_info['attachments']:
            # Extract and properly format all data
            file_id, created_at, filename, url = attachment
            filename = self.fix_filename(file_id, filename)
            local_filename = os.path.join(download_directory, filename)
            formatted_time = self.get_formatted_time(created_at)

            # Perform the actual download of each file
            if not os.path.exists(local_filename):
                print "Downloading {0} to {1} ...".format(filename, local_filename)
                urllib.urlretrieve(url, local_filename)

                # Check if file extraction is possible
                self.check_and_extract_files(download_directory, filename, local_filename, formatted_time)
                self.touch_file(formatted_time, local_filename)

	# Create PDF summary	
	pdf_lines = [
		"Ticket URL %s" % attachment_info["url"],
        	"From: %s" % attachment_info["from"],
                "Assigned To: %s" % attachment_info["user"],
                "Date Received: %s" % attachment_info["created_at"],
		"Date Completed: %s" % attachment_info["completed_on"],
		"",
                "Subject: %s" % attachment_info["name"],
		"",
                attachment_info["body"]
        ]
	#print pdf_lines
	with open(os.path.join(download_directory, "request"), "w") as req_file:
    		req_file.write('\n'.join(pdf_lines))
    		#req_file.write('\n'.join(pdf_lines))
	os.system("python pytext2pdf.py {0}".format(os.path.join(download_directory,"request")))
	os.remove(os.path.join(download_directory,"request"))
        return download_directory
