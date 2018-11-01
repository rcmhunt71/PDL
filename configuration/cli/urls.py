import PDL.logger.logger as pdl_log

log = pdl_log.Logger()


class UrlArgProcessing(object):

    REDUCED_LIST = 'reduced_list'
    TOTAL_DUP_LIST = 'total_dup_list'
    UNIQUE_DUP_LIST = 'unique_dup_list'
    PROTOCOL = 'https://'
    VALID = True
    INVALID = False

    @classmethod
    def process_url_list(cls, url_list, domain=None):
        """
        Split any combined URLs, verify all URLs are valid, and remove any duplicates

        :param url_list: List of URLs to process
        :param domain: Domain URLs should contain (www.abc.com)

        :return: List of valid, unique URLs

        """
        log.info("Number of entries (URLs) in list: {0}".format(len(url_list)))

        # Split and validate URLs (concatenated and/or invalid URLs), and check
        # for the correct domain in the host portion of the URL
        urls = UrlArgProcessing.split_urls(url_list, domain=domain)

        # Remove duplicates
        url_dict = UrlArgProcessing.reduce_url_list(urls)

        return url_dict[cls.REDUCED_LIST]

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

        log.info("Number of URLs in list: {0}".format(len(url_list)))
        log.info("Number of Unique URLs:  {0}".format(len(reduced_list)))
        log.info("Number of Duplicates:   {0}".format(len(total_dups)))
        log.info("Number of Unique Duplicates:  {0}".format(len(unique_dups)))

        return {cls.REDUCED_LIST: reduced_list,
                cls.TOTAL_DUP_LIST: total_dups,
                cls.UNIQUE_DUP_LIST: unique_dups}

    @classmethod
    def split_urls(cls, url_list, domain=None, delimiter=PROTOCOL):
        """
        Check for URLs that are not space delimited from the CLI. If found,
        split the URL into two URLs and add to the list.
        :param url_list: List of URLs to process
        :param domain: Domain expected within host portion of URL
        :param delimiter: Delimiter that indicates unique URLs, e.g. - space or comma

        :return: List of valid URLs

        """
        # Concatenate all entries into a space-delimited string
        num_urls_init = len(url_list)
        url_concat = ' '.join(url_list)

        # Split on delimiter (Catches concatenated http entries)
        # Rejoin with space delimiter (concatenated entries are now separate)
        url_temp = ' {0}'.format(delimiter).join(url_concat.split(delimiter))
        if url_concat != url_temp:
            log.debug("Concatenated URL Found (Delimiter: {delim}) - Fixed".format(
                delim=delimiter))

        # Ignore '' urls, they are not valid, and the splitting generates a ''
        # at the front of each element in a split list.
        url_temp_list = [url for url in url_temp.split(' ') if url != '']

        log.info("Number of concatenations: {0}".format(len(url_temp_list) - num_urls_init))

        # Check the validity of all existing URLs and classify based on validity.
        urls = {cls.VALID: list(),
                cls.INVALID: list()}

        for url in url_temp_list:
            urls[UrlArgProcessing.validate_url(url, domain=domain)].append(url)

        log.info("Number of VALID URLs in list: {0}".format(
            len(urls[cls.VALID])))
        log.info("Number of INVALID URLs in list: {0}".format(
            len(urls[cls.INVALID])))

        return urls[cls.VALID]

    @classmethod
    def validate_url(cls, url, domain=None, protocol=PROTOCOL):
        """
        Verify URL starts with delimited, and has additional URL info.

        :param url: URL
        :param domain: Expected/Required Domain
        :param protocol: protocol prefix for URL

        :return: Boolean; True = Valid URL

        """
        valid = (url.lower().startswith(protocol.lower()) and
                 url.lower() != protocol.lower())

        if domain is not None:
            valid = valid and domain.lower() in url.lower()

        log.debug("{status}: URL='{url}'".format(
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
