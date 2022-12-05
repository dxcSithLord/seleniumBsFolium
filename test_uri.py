'''
    Description: Ref ref https://www.rfc-editor.org/rfc/rfc3986#appendix-B
    To test for a URL, the following regular expression maps to URI components
    based on the RFC3986:
       ^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?
       12            3  4          5       6  7        8 9

    The numbers in the second line above are only to assist readability;
    they indicate the reference points for each subexpression (i.e., each
    paired parenthesis).  We refer to the value matched for subexpression
    <n> as $<n>.  For example, matching the above expression to

      http://www.ics.uci.edu/pub/ietf/uri/#Related

    results in the following subexpression matches:

      $1 = http:
      $2 = http
      $3 = //www.ics.uci.edu
      $4 = www.ics.uci.edu
      $5 = /pub/ietf/uri/
      $6 = <undefined>
      $7 = <undefined>
      $8 = #Related
      $9 = Related
    functions:
    uri_match - returns true is uri contains http[s]:/site as part of the url
'''
import re     # regular expressions

RFC3986_re = r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'


def uri_match(href):
    """
    Function to return true is the href contains http, https and a website
    href - string argument containing uri to be inspected
    returns true if starts with http and contains a site reference
    """
    url_re = re.compile(RFC3986_re)
    url_list = url_re.findall(href)
    ret_val = False
    if len(url_list) > 1:
        ret_val = True
    else:
        if 'http' in url_list[0][1] and url_list[0][2] != '':
            ret_val = True
    return ret_val

