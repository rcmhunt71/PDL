import pprint


class CliArgProcessing(object):

    REDUCED_LIST = 'reduced_list'
    TOTAL_DUP_LIST = 'total_dup_list'
    UNIQUE_DUP_LIST = 'unique_dup_list'
    DELIMITER = 'https://'

    @classmethod
    def reduce_url_list(cls, url_list):
        """
        Remove any duplicates from the list. Also able to report
        all duplicates found (as debug).
        :return: dictionary of:
            * reduced_list: List of unique elements
            * total_dup_list: List of all duplicates
            * unique_dup_list: List of all unique duplicates

        """
        results = dict()
        results[cls.REDUCED_LIST] = list(set(url_list))
        results[cls.TOTAL_DUP_LIST] = [url for n, url in enumerate(url_list) if url in url_list[:n]]
        results[cls.UNIQUE_DUP_LIST] = list(set(results[cls.TOTAL_DUP_LIST]))
        return results

    @classmethod
    def split_urls(cls, url_list, delimiter=DELIMITER):
        """
        Check for URLs that are not space delimited from the CLI. If found, split the
        URL into two URLs and add to the list.
        :param url_list:
        :param delimiter:
        :return: List of valid URLs

        """
        debug = False
        if debug:
            print("List:\n{0}\n\n".format(pprint.pformat(url_list)))

        # Concatenate all entries into a space-delimited string
        url_concat = ' '.join(url_list)

        # Split on delimiter (Catches concatenated http entries)
        # Rejoin with space-delimiting (concatenated entries are now separate)
        url_temp = ' {0}'.format(delimiter).join(url_concat.split(delimiter))
        if debug and url_concat != url_temp:
            print("Original URL: {0}".format(url_concat))
            print("Updated URL: {0}".format(url_temp))

        new_url_list = []
        for url in url_temp.split(' '):
            if CliArgProcessing.validate_url(url):
                new_url_list.append(url)

        return new_url_list

    @classmethod
    def validate_url(cls, url, delimiter=DELIMITER):
        """
        Verify URL starts with delimited, and has additional URL info.

        TODO: Check for domain. <protocol>://<domain>/[[resources]..]
        :param url: URL
        :param delimiter: protocol prefix for URL
        :return: Boolean; True = Valid URL

        """

        # TODO: In place until debug flag and logging is in place
        debug = False
        if debug:
            print("URL: {url}".format(url=url))
            print("Delimiter: {delimiter}".format(delimiter=delimiter))

        valid = url.lower().startswith(delimiter.lower()) and url.lower() != delimiter.lower()
        return valid

    @classmethod
    def list_urls(cls, url_list):
        """
        Generate multi-line string of URLs in list
        :param url_list: List of URLs
        :return: multi-line string

        """
        url_list_string = ''
        for index, url in enumerate(url_list):
            url_list_string += "{counter}) {curr_url}\n".format(counter=index + 1, curr_url=url)
        return url_list_string
