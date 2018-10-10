import PDL.logger.logger as pdl_log

log = pdl_log.Logger()


class CliArgProcessing(object):

    REDUCED_LIST = 'reduced_list'
    TOTAL_DUP_LIST = 'total_dup_list'
    UNIQUE_DUP_LIST = 'unique_dup_list'
    DELIMITER = 'https://'

    @classmethod
    def reduce_url_list(cls, url_list):
        """
        Remove any duplicates from the list.

        TODO: Log all duplicates found; currently only counts are reported.

        :return: dictionary of:
            * reduced_list: List of unique elements
            * total_dup_list: List of all duplicates
            * unique_dup_list: List of all unique duplicates

        """
        reduced_list = list(set(url_list))
        total_dups = [url for n, url in enumerate(url_list) if url in url_list[:n]]
        unique_dups = list(set(total_dups))

        log.debug("Number of URLs on CLI: {0}".format(len(url_list)))
        log.debug("Number of Unique URLs: {0}".format(reduced_list))
        log.debug("Number of Duplicates:  {0}".format(total_dups))
        log.debug("Number of Unique Duplicates:  {0}".format(unique_dups))

        return {cls.REDUCED_LIST: reduced_list,
                cls.TOTAL_DUP_LIST: total_dups,
                cls.UNIQUE_DUP_LIST: unique_dups}

    @classmethod
    def split_urls(cls, url_list, delimiter=DELIMITER):
        """
        Check for URLs that are not space delimited from the CLI. If found,
        split the URL into two URLs and add to the list.
        :param url_list:
        :param delimiter:

        :return: List of valid URLs

        """
        # Concatenate all entries into a space-delimited string
        url_concat = ' '.join(url_list)

        # Split on delimiter (Catches concatenated http entries)
        # Rejoin with space delimiter (concatenated entries are now separate)
        url_temp = ' {0}'.format(delimiter).join(url_concat.split(delimiter))
        if url_concat != url_temp:
            log.debug("Concatenated URL Found (Delimiter: {delim})".format(
                delim=delimiter))
            log.debug("\tOriginal URL: {0}".format(url_concat))
            log.debug("\tUpdated URLs: {0}".format(url_temp))

        # Ignore '' urls, they are not valid, and the splitting generates a ''
        # at the front of each element in a split list.

        return [url for url in url_temp.split(' ') if url is not '' and
                CliArgProcessing.validate_url(url)]

    @classmethod
    def validate_url(cls, url, delimiter=DELIMITER):
        """
        Verify URL starts with delimited, and has additional URL info.

        TODO: Check for domain. <protocol>://<domain>/[[resources]..]

        :param url: URL
        :param delimiter: protocol prefix for URL

        :return: Boolean; True = Valid URL

        """
        valid = (url.lower().startswith(delimiter.lower()) and
                 url.lower() != delimiter.lower())

        log.debug("{status}: URL: {url}".format(
            status="VALID" if valid else "INVALID", url=url))

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
            url_list_string += "{counter}) {curr_url}\n".format(
                counter=index + 1, curr_url=url)
        return url_list_string
