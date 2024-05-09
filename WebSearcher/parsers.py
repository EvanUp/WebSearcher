from . import webutils
from .component_classifier import classify_type
from .component_parsers import type_functions
from .extractors import extract_components
from .models import BaseResult
from .logger import Logger
log = Logger().start(__name__)

import traceback
from bs4 import BeautifulSoup


def get_component_parser(cmpt_type:str, cmpt_funcs:dict=type_functions) -> callable:
    """Returns the parser for a given component type"""
    try:
        return cmpt_funcs[cmpt_type]
    except KeyError as e:
        return not_implemented


def not_implemented(cmpt) -> list:
    """Placeholder function for component parsers that are not implemented"""
    parsed = BaseResult(type=classify_type(cmpt), sub_rank=0).model_dump()
    parsed['error'] = 'not implemented'
    return [parsed]


def parse_component(cmpt, cmpt_type:str = '', cmpt_rank:int = 0) -> list:
    """Parse a SERP component
    
    Args:
        cmpt (bs4 object): A parsed SERP component
        cmpt_type (str, optional): The type of component it is
        cmpt_rank (int, optional): The rank the component was found
    
    Returns:
        dict: The parsed results and/or subresults
    """

    # Classify Component
    cmpt_type = cmpt_type if cmpt_type else classify_type(cmpt)
    assert cmpt_type, 'Null component type'

    # Return unknown components
    if cmpt_type == 'unknown':
        parsed = BaseResult(type='unknown', sub_rank=0).model_dump()
        parsed['cmpt_rank'] = cmpt_rank
        return [parsed]

    # Parse component
    try:
        parser = get_component_parser(cmpt_type)
        parsed_cmpt = parser(cmpt)
        
        # Add cmpt rank to parsed
        if isinstance(parsed_cmpt, list):
            for sub_rank, sub in enumerate(parsed_cmpt):
                sub.update({'sub_rank':sub_rank, 'cmpt_rank':cmpt_rank})
        elif isinstance(parsed_cmpt, dict):
            parsed_cmpt.update({'sub_rank':0, 'cmpt_rank':cmpt_rank})
        else:
            raise TypeError(f'Parsed component must be list or dict: {parsed_cmpt}')

    except Exception:
        log.exception('Parsing Exception')
        err = traceback.format_exc()
        return [{'type':cmpt_type, 'cmpt_rank':cmpt_rank, 'error':err}]

    return parsed_cmpt


def parse_serp(serp:BeautifulSoup, serp_id:str = None, crawl_id:str = None, 
               verbose:bool = False, make_soup:bool = False) -> list:
    """Parse a Search Engine Result Page (SERP)
    
    Args:
        serp (html): raw SERP HTML or BeautifulSoup
        serp_id (str, optional): A SERP-level key, hash generated by default
        verbose (bool, optional): Log details about each component parse
    
    Returns:
        list: A list of parsed results ordered top-to-bottom and left-to-right
    """

    soup = webutils.make_soup(serp) if make_soup and type(serp) is not BeautifulSoup else serp
    assert type(soup) is BeautifulSoup, 'Input must be BeautifulSoup'

    # Extract components
    cmpts = extract_components(soup)

    # Classify and parse components
    parsed = []
    if verbose: 
        log.info(f'Parsing SERP {serp_id}')
        
    for cmpt_rank, (cmpt_loc, cmpt) in enumerate(cmpts):
        cmpt_type = classify_type(cmpt) if cmpt_loc == 'main' else cmpt_loc
        
        # Ignore directions component
        if cmpt_type == 'directions':
            continue

        if verbose: 
            log.info(f'{cmpt_rank} | {cmpt_type}')
        parsed_cmpt = parse_component(cmpt, cmpt_type=cmpt_type, cmpt_rank=cmpt_rank)
        assert isinstance(parsed_cmpt, list), \
            f'Parsed component must be list: {parsed_cmpt}'
        parsed.extend(parsed_cmpt)

    # Set SERP-level attributes
    serp_attrs = {}
    if serp_id: 
        serp_attrs['serp_id'] = serp_id
    if crawl_id:
        serp_attrs['crawl_id'] = crawl_id

    for serp_rank, p in enumerate(parsed):
        p['serp_rank'] = serp_rank
        p.update(serp_attrs)
        
    return parsed
