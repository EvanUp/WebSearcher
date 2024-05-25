from ..components import Component, ComponentList

from .ads import parse_ads
from .available_on import parse_available_on
from .banner import parse_banner
from .discussions_and_forums import parse_discussions_and_forums
from .general import parse_general_results
from .general_questions import parse_general_questions
from .images import parse_images
from .knowledge import parse_knowledge_panel

from .top_stories import parse_top_stories
from .latest_from import parse_latest_from
from .local_news import parse_local_news
from .perspectives import parse_perspectives

from .local_results import parse_local_results
from .map_results import parse_map_results
from .news_quotes import parse_news_quotes
from .people_also_ask import parse_people_also_ask
from .scholarly_articles import parse_scholarly_articles
from .searches_related import parse_searches_related
from .shopping_ads import parse_shopping_ads
from .top_image_carousel import parse_top_image_carousel
from .twitter_cards import parse_twitter_cards
from .twitter_result import parse_twitter_result
from .videos import parse_videos
from .view_more_news import parse_view_more_news

from .footer import Footer, parse_footer
from .knowledge_rhs import parse_knowledge_rhs

# Component details dataframe
columns = ['type', 'func', 'label']
component_parser_catalogue = [
    ('ad', parse_ads, 'Ad'),
    ('available_on', parse_available_on, 'Available On'),
    ('banner', parse_banner, 'Banner'),
    ('discussions_and_forums', parse_discussions_and_forums, 'Discussions & Forums'),
    ('general', parse_general_results, 'General'),
    ('general_questions', parse_general_questions, 'General Questions'),
    ('images', parse_images, 'Images'),
    ('knowledge', parse_knowledge_panel, 'Knowledge'),
    ('latest_from', parse_latest_from, 'Latest From'),
    ('local_news', parse_local_news, 'Local News'),
    ('local_results', parse_local_results, 'Local Results'),
    ('map_results', parse_map_results, 'Map Results'),
    ('news_quotes', parse_news_quotes, 'News Quotes'),
    ('people_also_ask', parse_people_also_ask, 'People Also Ask'),
    ('perspectives', parse_perspectives, 'Perspectives & Opinions'),
    ('scholarly_articles', parse_scholarly_articles, 'Scholar Articles'),
    ('searches_related', parse_searches_related, 'Related Searches'),
    ('shopping_ads', parse_shopping_ads, 'Shopping Ad'),
    ('top_image_carousel', parse_top_image_carousel, 'Top Image Carousel'),
    ('top_stories', parse_top_stories, 'Top Stories'),
    ('twitter_cards', parse_twitter_cards, 'Twitter Cards'),
    ('twitter_result', parse_twitter_result, 'Twitter Result'),
    ('videos', parse_videos, 'Videos'),
    ('view_more_news', parse_view_more_news, 'View More News'),
    ('footer', parse_footer, 'Footer'),
    ('knowledge_rhs', parse_knowledge_rhs, 'Knowledge RHS'),
]

# Format {type: function}
type_functions = {i[0]:i[1] for i in component_parser_catalogue}

# Format {type: label}
type_labels = {i[0]:i[2] for i in component_parser_catalogue}


def get_component_parser(cmpt:Component, cmpt_funcs:dict=type_functions) -> callable:
    """Returns the parser for a given component type"""
    if cmpt.section == 'footer':
        return Footer.get_parser(cmpt.type)
    else:
        if cmpt.type in cmpt_funcs:
            return cmpt_funcs[cmpt.type]
        elif cmpt.type == 'unknown':
            return parse_unknown
        else:
            return parse_not_implemented


def parse_unknown(cmpt: Component) -> list:
    parsed_result = {'type': cmpt.type,
                     'cmpt_rank': cmpt.cmpt_rank,
                     'text': cmpt.elem.get_text("<|>", strip=True) if cmpt.elem else None}
    return [parsed_result]


def parse_not_implemented(cmpt: Component) -> list:
    """Placeholder function for component parsers that are not implemented"""
    parsed_result = {'type': cmpt.type,
                     'cmpt_rank': cmpt.cmpt_rank,
                     'text': cmpt.elem.get_text("<|>", strip=True),
                     'error': 'not implemented'}
    return [parsed_result]
