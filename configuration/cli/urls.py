from typing import Dict, List

import PDL.logger.logger as pdl_log

log = pdl_log.Logger()


class UrlArgProcessing(object):

    """
    Purpose: A series of utilities (static methods) to take a list of
    potential URL strings, and remove:
      + duplicates,
      + non-URL strings
      + Multiple URLs that are concatenated
        + https://foo.com/index.htmlhttp://foo.com/index2.html = 2 URLs

    """
    REDUCED_LIST = 'reduced_list'
    TOTAL_DUP_LIST = 'total_dup_list'
    UNIQUE_DUP_LIST = 'unique_dup_list'
    PROTOCOL = 'https://'
    VALID = True
    INVALID = False

    @classmethod
    def process_url_list(cls, url_list: List[str], domains: List[str] = None) -> List[str]:
        """
        Split any combined URLs, verify all URLs are valid, and remove any duplicates

        :param url_list: List of URLs to process
        :param domains: List of possible domains URLs should contain

        :return: List of valid, unique URLs

        """
        log.info(f"Number of entries (URLs) in list: {len(url_list)}")

        domains = domains or list()

        # Split and validate URLs (concatenated and/or invalid URLs), and check
        # for the correct domains in the host portion of the URL
        urls = UrlArgProcessing.split_urls(url_list, domains=domains)

        # Remove duplicates
        url_dict = UrlArgProcessing.reduce_url_list(urls)

        return url_dict[cls.REDUCED_LIST]

    @classmethod
    def reduce_url_list(cls, url_list: List[str]) -> Dict[str, List[str]]:
        """
        Remove any duplicates from the list. Log all duplicates (debug).

        :return: dictionary of:
            * reduced_list: List of unique elements
            * total_dup_list: List of all duplicates
            * unique_dup_list: List of all unique duplicates

        """
        reduced_list = list(set(url_list))
        total_dups = [url for n, url in enumerate(url_list) if
                      url in url_list[:n]]
        unique_counts = UrlArgProcessing.counts_of_each_dup(total_dups)
        unique_dups = unique_counts.keys()

        log.info(f"Number of URLs in list: {len(url_list)}")
        log.info(f"Number of Unique URLs:  {len(reduced_list)}")
        log.info(f"Number of Duplicates:   {len(total_dups)}")
        log.info(f"Number of Unique Duplicates:  {len(unique_dups)})")

        # Log counts of duplicates per duplicate URL
        if len(total_dups) > 0:
            log.debug("Count of Each Unique Duplicate:")
            for url, count in unique_counts.items():
                log.debug(f"DUP: {url}: Count:  {count}")

        return {cls.REDUCED_LIST: reduced_list,
                cls.TOTAL_DUP_LIST: total_dups,
                cls.UNIQUE_DUP_LIST: unique_dups}

    @classmethod
    def counts_of_each_dup(cls, duplicates: List[str]) -> Dict[str, int]:
        """
        Tally the counts of each unique duplicate.
        :param duplicates: list of duplicate URLs
        :return: dictionary of tallied urls (k: unique_urls, v: count)

        """
        return dict([(url, duplicates.count(url)) for url in
                     list(set(duplicates))])

    @classmethod
    def split_urls(cls, url_list: List[str], domains: List[str] = None,
                   delimiter: str = PROTOCOL) -> List[str]:
        """
        Check for URLs that are not space delimited from the CLI. If found,
        split the URL into two URLs and add to the list.
        :param url_list: List of URLs to process
        :param domains: List of allowed domains within host portion of URL
        :param delimiter: Delimiter that indicates unique URLs,
                             e.g. - space or comma

        :return: List of valid URLs

        """
        # Concatenate all entries into a space-delimited string
        num_urls_init = len(url_list)
        url_concat = ' '.join(url_list)
        domains = domains or list()

        # Split on delimiter (Catches concatenated http entries)
        # Rejoin with space delimiter (concatenated entries are now separate)
        url_temp = ' {0}'.format(delimiter).join(url_concat.split(delimiter))
        if url_concat != url_temp:
            msg = f"Concatenated URL Found (Delimiter: {delimiter}) - Fixed"
            log.debug(msg)

        # Ignore '' urls, they are not valid, and the splitting generates a ''
        # at the front of each element in a split list.
        url_temp_list = [url for url in url_temp.split(' ') if url != '']

        diff = len(url_temp_list) - num_urls_init
        log.info(f"Number of concatenations: {diff}")

        # Check the validity of all existing URLs and classify based on validity
        urls = {cls.VALID: list(),
                cls.INVALID: list()}

        for url in url_temp_list:
            urls[UrlArgProcessing.validate_url(
                url, domains=domains)].append(url)

        log.info(f"Number of VALID URLs in list: {len(urls[cls.VALID])}")
        log.info(f"Number of INVALID URLs in list: {len(urls[cls.INVALID])}")

        return urls[cls.VALID]

    @classmethod
    def validate_url(cls, url: str, domains: List[str] = None, protocol: str = PROTOCOL):
        """
        Verify URL starts with delimited, and has additional URL info.

        :param url: URL
        :param domains: List of expected/required domains in URL
        :param protocol: protocol prefix for URL

        :return: Boolean; True = Valid URL

        """
        domains = domains or list()

        log.debug(f'Checking for domains: {domains}')

        valid = (url.lower().startswith(protocol.lower()) and
                 url.lower() != protocol.lower())

        if not valid:
            msg = (f"Invalid URL: '{url.lower()}'. "
                   f"Did not match expected protocol(s): '{protocol.lower()}'")
            log.warn(msg)

        # Filter out 'None' domains... it is an invalid domain.
        domains = [x for x in domains if x is not None]

        if domains and valid:
            if any(x.lower() in url.lower() for x in domains):
                valid = True
                log.debug('Matching domain found.')
            else:
                valid = False
                msg = ("Invalid URL: '{0}'. "
                       "Did not match expected domains: '{1}'")
                log.warn(msg.format(url.lower(), ', '.join(domains)))

        log.debug("{status}: URL='{url}'".format(
            status="VALID" if valid else "INVALID", url=url))

        return valid

    @classmethod
    def list_urls(cls, url_list: List[str]) -> str:
        """
        Generate multi-line string of URLs in list
        :param url_list: List of URLs

        :return: multi-line string

        """
        fmt = "{ctr:>3}: {url}"

        url_list = [fmt.format(ctr=index + 1, url=url) for index, url
                    in enumerate(url_list)]
        return '\n'.join(url_list)
