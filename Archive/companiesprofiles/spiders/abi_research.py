from companiesprofiles.spiders.BaseSpider import BaseCrawlSpider

class AbiResearchSpider(BaseCrawlSpider):
    name = "abi_research"
    allowed_domains = ["abiresearch.com"]
    start_urls = (
        'https://www.abiresearch.com/staff/analysts/',
    )

    company = "ABI Research"
    company_url = "https://www.abiresearch.com"

    test_mode = True
    test_profile_url = "https://www.abiresearch.com/staff/bio/dominique-bonte/"
    test_profile_url = "https://www.abiresearch.com/staff/bio/stuart-carlaw/"

    xpaths = {
      "profiles": {
            "xpath": "//a[contains(@href, '/staff/bio/')]/@href"
      },
      "bio_education": {
            "xpath": "//strong[contains (., 'Education')]/following-sibling::span|//p[following::h2[contains(.,'Blogs by')] and preceding::h2[contains (., 'Education')]]|//p[following::h2[contains(.,'Blogs by')] and preceding::p[contains (., 'Education')]]|//strong[contains (., 'Education')]/following-sibling::text()|//p[contains (., 'Education')]/following-sibling::p|//h2[contains (., 'Education')]/following-sibling::p[1]"
      },
      "biography": {
            "xpath": "//strong[contains (., 'Research Focus')]/following-sibling::span|//p["
                     "following::h2[contains(.,'Past Experience, Memberships, Accolades and Media')] and preceding::h2[contains (., 'Research Focus')]]|//p[following::p[contains(.,'Past Experience, Memberships, Intellectual Property')] and preceding::p[contains (., 'Research Focus')]]|//p[following::h2[contains(.,'Experience')] and preceding::h2[contains (., 'Research Focus')]]|//p[following::*[contains(.,'Experience')] and preceding::*[contains (., 'Research Focus')]]|//strong[contains (., 'Research Focus')]/following-sibling::text()|//h2[contains (., 'Research Focus')]/following-sibling::p[1]",
            "xpath_fallback": "//div[@id='main-content-with-sidebar']/p[count(preceding::h2)=0]"
      },
      "name_full": {
            "xpath": "//p[@class=\"name\"]"
      },
      "photo_url": {
            "xpath": "//img[@class=\"headshot\"]"
      },
      "previous_bio": {
            "xpath": "//strong[contains (., 'Past Experience, Memberships, Accolades and Media ')]/following-sibling::span|//p[following::h2[contains(.,'Education')] and preceding::h2[contains (., 'Past Experience, Memberships, Accolades and Media')]]|//p[following::p[contains(.,'Education')] and preceding::p[contains (., 'Past Experience, Memberships, Intellectual Property')]]|//p[following::h2[contains(.,'Education')] and preceding::h2[contains (., 'Experience')]]|//strong[contains (., 'Past Experience, Membership, Accolades and Media')]/following-sibling::text()"
      },
      "taxonomy_market": {
            "regex": "(?<=,).*",
            "xpath": "//p[@class=\"title\"]"
      },
      "taxonomy_topics": {
            "xpath": "//ul[@class='list-unstyled'][2]/li"
      },

      "title": {
            "xpath": "//p[@class=\"title\"]"
      },
      "twitter": {
            "regex": "[^/]+$",
            "xpath": "//a[contains (@href , 'twitter.com')]/@href"
      }
}