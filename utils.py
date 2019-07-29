#!/usr/bin/env python
# coding=utf-8

import os, logging, mechanize, urlparse, json, cookielib, getpass
from bs4 import BeautifulSoup as BS

url = 'https://siac.ufba.br/SiacWWW/Welcome.do'


def initialize_browser():
    """Configurações para contornar os cookies, robots.txt e outros para fingir ser um browser normal."""
    cookiejar = cookielib.LWPCookieJar()
    opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookiejar))
    mechanize.install_opener(opener)
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.set_handle_redirect(True)
    browser.set_cookiejar(cookiejar)
    browser.set_handle_equiv(True)
    browser.set_handle_referer(True)
    browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=2)
    browser.addheaders = [('User-agent', 'Google Chrome')]
    return browser, cookiejar  

def login_to_site(br):
    br.open(url)
    cpf = (raw_input('Digite seu CPF do SIAC : '))
    #senha = (raw_input('Digite sua senha do SIAC : '))
    senha = getpass.getpass("Digite sua senha : ")
    br.select_form(nr=0)
    br['cpf'] = (cpf)
    br['senha'] = senha
    br.submit()
    print ('Fazendo login no siac ...')
    resposta = br.response().read()