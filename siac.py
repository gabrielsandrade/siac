#!/usr/bin/env python
# coding=utf-8
import mechanize, urlparse, os, logging, utils, getpass
from bs4 import BeautifulSoup as BS
import pandas as pd

### LINKS

obrigatorias_link = 'https://siac.ufba.br/SiacWWW/ConsultarDisciplinasObrigatorias.do'
optativas_link = 'https://siac.ufba.br/SiacWWW/ConsultarDisciplinasOptativas.do'
curriculo_link  = 'https://siac.ufba.br/SiacWWW/ConsultarCurriculoCurso.do'
cr_link = 'https://siac.ufba.br/SiacWWW/ConsultarCoeficienteRendimento.do'
curso_link = 'https://siac.ufba.br/SiacWWW/ConsultarCurriculoCurso.do'



def main():
    url = 'https://siac.ufba.br/SiacWWW/Welcome.do'
    br, cj = utils.initialize_browser()
    utils.login_to_site(br)

    cr_page = br.open(cr_link).read()
    curso_page = br.open(curso_link).read()
    curso_parse = BS(curso_page, 'html5lib')
    tabela = curso_parse.find_all('table', attrs={'class':'simple'})[0]
    curso_nome = tabela.find_all('td')[0]
    curso_codigo = curso_nome.text[:6]
    
    cr = BS(cr_page, 'html5lib')
    table = (cr.find('table', attrs={'class':'simple'})).encode('utf-8')
    df = pd.read_html(str(table).decode('utf-8'))
    df = df[0]
    aprovadas = (df[df['RES'] != 'RR'])[:-1] #Disciplinas cujo resultado é 'AP'
    aproveitadas = df[df['RES'] == 'DI'] #Disciplinas que foram aproveitadas, RES = DI

    grade_curso = br.open('https://siac.ufba.br/SiacWWW/ConsultarComponentesCurricularesCursados.do').read()
    grade_curso_parse = BS(grade_curso,'html5lib')
    grade_curso_page = grade_curso_parse.find('table', attrs={'class':'corpoHistorico'}).encode('utf-8')
    tabelaDiscente = grade_curso_parse.find('table', attrs={'class':'cabecalho'}).encode('UTF-8')
    tabelaDiscente = pd.read_html(str(tabelaDiscente).decode('UTF-8'))[0]
    
    print('\n--------------------------------\n')
    print (tabelaDiscente[1][0])
    print (tabelaDiscente[0][0])
    print ('Curso : {}'.format(curso_nome.text[9:].encode('utf-8')))
    print ('Código do curso : {}'.format(curso_codigo))
    print (tabelaDiscente[0][1])
    print (tabelaDiscente[2][3])
    print('\n--------------------------------\n')

    tabela_disciplinas = pd.read_html(str(grade_curso_page).decode('utf-8'))[0]
    aprovadas.dropna(how='any', inplace=True)
    aprovadas = [tabela_disciplinas[tabela_disciplinas['RES'] != 'RR']][0]
    aprovadas = [aprovadas[aprovadas['RES'] != '--']][0]
    chOb = 0

    for disciplina in (aprovadas[aprovadas['NT'] == 'OB']).iterrows():
        try:
            chOb += int(disciplina[1][3])
        except:
            continue

    obrigatoriasAprovadas = (len(aprovadas['Componentes Curriculares'].unique()))
    qtdObAprovadas = len(aprovadas[aprovadas['NT'] == 'OB'])
    obrigatorias = br.open(obrigatorias_link).read()
    obrigatorias = BS(obrigatorias, 'html5lib')
    tabelaObrigatorias = obrigatorias.find('table', attrs={'class':'simple'}).encode('utf-8')
    dfTabelaObrigatorias = pd.read_html(str(tabelaObrigatorias).decode('utf-8'))[0]
    totalObrigatorias = (dfTabelaObrigatorias['Componente Curricular'].count())

    for linha in (aprovadas.iterrows()):
        try:            
            dfTabelaObrigatorias = dfTabelaObrigatorias[dfTabelaObrigatorias['Código'.decode('UTF-8')] != linha[1][1]]
        except:
            pass

    dfTabelaObrigatorias = dfTabelaObrigatorias.loc[:, ~dfTabelaObrigatorias.columns.str.contains('^Unnamed')]
    dfTabelaObrigatorias.dropna(how='any', inplace = True)
    dfTabelaObrigatorias = dfTabelaObrigatorias.drop(columns = ['Natureza'])

    curriculo = br.open(curriculo_link).read()
    curriculo_parse = BS(curriculo, 'html5lib')
    curriculo_tabela = curriculo_parse.find_all('table', attrs={'class':'simple'})[1].encode('utf-8')
    curriculo_df = pd.read_html(str(curriculo_tabela).decode('utf-8'))[0]

    cargaHorariaOb = int(curriculo_df[curriculo_df['Natureza'] == 'Obrigatoria']['Carga Horária'.decode('utf-8')])
    cargaHorariaOp = int(curriculo_df[curriculo_df['Natureza'] == 'Optativa']['Carga Horária'.decode('utf-8')])
    
    chTotal = int(aprovadas[-1:]['CH'])
    cargaHorariaTotal = cargaHorariaOb + cargaHorariaOp
    chOp = chTotal - chOb
    porcentagemCH = 100 * float (chOb)/ float (cargaHorariaOb)
    

    porcentagemAprovadas = 100 * float(qtdObAprovadas)/float(totalObrigatorias)
    porcentagemOptativa = 100 * float (chOp) / float (cargaHorariaOp)
    porcentagemTotal = 100 * float(chTotal) / float(cargaHorariaTotal)
    
    print ("{} de {} disciplinas obrigatórias ({:.2f}%).".format(qtdObAprovadas, totalObrigatorias, porcentagemAprovadas))
    print ("{} de {} horas obrigatórias ({:.2f}%).".format(chOb, cargaHorariaOb, porcentagemCH))
    print ("{} de {} horas optativas ({:.2f}%).".format(chOp, cargaHorariaOp, porcentagemOptativa))
    print ("{} de {} da carga horária total do curso ({:.2f}%).".format(chTotal, cargaHorariaTotal, porcentagemTotal))
    print ('\n------- Disciplinas obrigatórias que ainda não foram feitas -------\n')
    print (dfTabelaObrigatorias)
    
    #export_csv = df.to_csv('Disciplinas-feitas.csv', index=False, encoding='utf-16')

if __name__ == '__main__':
    main ()