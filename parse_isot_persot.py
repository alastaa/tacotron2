import re
import os
from glob import glob
import argparse
import pdb
import chardet


def prefix_and_text_from_line(line):
	prefix_regex = r'(.*_)?[0-9]{4}'
	regex_result = re.search(prefix_regex, line)
	prefix = regex_result.group() if regex_result else None
	text = line.replace(prefix, '').strip() if prefix else line
	return prefix, text


def wav_dir_from_textfile(textfile):
    file_to_wavdir_mapping = {
        'long_01n_lombard_rich.txt': 'long_01n_lombard',
        'long_01n_whisp_rich.txt': 'long_01n_whisp',
        'long_01n_whisp_quotes.txt': 'long_01n_whisp',
        'long_01n_lombard_quotes.txt': 'long_01n_lombard',
        'long_01n_lombard_test.txt': 'long_01n_lombard',
        'long_01m_greets&diags.txt': 'long_01m_greetsndiags',
        'long_02m_num.txt': 'long_02m_nums',
        }
    base_dir = os.path.abspath(os.path.join(textfile , os.pardir, os.pardir))
    textfilename = os.path.basename(textfile.replace('.txt', ''))
    if file_to_wavdir_mapping.get(os.path.basename(textfile)):
        wav_dir = file_to_wavdir_mapping.get(os.path.basename(textfile))
    else:
        wav_dir = file_to_wavdir_mapping.get(textfilename, textfilename)
    if not os.path.isdir(os.path.join(base_dir,wav_dir)):
        wav_dir = "_".join(wav_dir.split('_')[:-1])
    if not os.path.isdir(os.path.join(base_dir,wav_dir)):
        raise ValueError
    return os.path.join(base_dir, wav_dir)


def find_match(prefix, wav_files, c):
    for wav_file in wav_files:
        if prefix in wav_file:
            return wav_file
    raise ValueError


'''
long_01m_fact.txt
    1. added newline to end of row 109
    2. added newline to end of row 175
    3. removed line 221
    4. added newline to end of row 235
    5. added newline to end of row 344

'''


def get_wav_files(wav_dir, textfile, filter):
    filters = {
        'long_01n_lombard_rich.txt': 'rich',
        'long_01n_whisp_rich.txt': 'rich',
        'long_01n_whisp_quotes.txt': 'quotes',
        'long_01n_lombard_quotes.txt': 'quotes',
        'long_01n_lombard_test.txt': 'test'
        }
    wav_files = sorted(map(os.path.basename, glob(wav_dir+'/*.wav')))
    wav_files = [f for f in wav_files if filter in f]
    return wav_files


def get_linebreak(content):
    tmp_count = re.findall('\n', content)
    b1_count = re.findall('\r\n', content)
    b2_count = tmp_count-b1_count



def handle_textfile2(textfile):
    metadata = {
        'long_01n_fact.txt': {'missing_lines': [222,223,224]},
        'long_01n_names.txt': {'missing_lines': [22], 'missing_wavs': [22,23]},
        'long_01n_prose_long.txt': {'missing_lines': [141,142,203,204,296, 388, 389, 407, 408, 429, 430], 'missing_wavs': [203,204,294,295, 309, 389, 390, 407, 408, 429]},
        'long_01m_prose_short.txt': {'missing_lines': [139,140], 'missing_wavs': [140]},
        'long_01m_prose_long.txt': {'missing_lines': [236,237], 'missing_wavs': [236]},
        'long_01m_names.txt': {'missing_wavs': [61]},
        'long_01m_greets&diags.txt': {'wavlist_modification': lambda x: x[34:-1]+x[:33]},
        'long_03n_quotes.txt': {'missing_lines': [100,101]},
        'long_03n_whisp_quotes.txt': {'missing_lines': [19]},
        'long_03n_fact.txt': {'missing_lines': [29]},
        'long_02n_prose_long.txt': {'missing_lines': [196]},
        'long_02n_rich.txt': {'missing_lines': [11]},
        'long_02m_fact.txt': {'missing_lines': [88]},
        'long_03m_prose_short.txt': {'missing_lines': [149,150], 'missing_wavs': [149]},
    }
    filters = {
        'long_01n_lombard_rich.txt': 'rich',
        'long_01n_whisp_rich.txt': 'rich',
        'long_01n_whisp_quotes.txt': 'quotes',
        'long_01n_lombard_quotes.txt': 'quotes',
        'long_01n_lombard_test.txt': 'test',
        'long_01m_names.txt': 'names_',
        }

    linebreaks = {
        'long_01m_fact.txt': '\n\r\n|\r\n\n',
        'long_01m_prose_short.txt': '\n\r\n|\r\n\n|\r\n'
    }

    textfilename = os.path.basename(textfile)
    pairs = []
    file_ = open(textfile,'rb')
    binary_content = file_.read()
    encoding = chardet.detect(binary_content)['encoding']
    file_content = binary_content.decode(encoding)
    linebreak = linebreaks.get(textfilename, '\r\n')
    #lines = file_content.split(linebreak)
    lines = re.split(linebreak, file_content)
    if len(lines) < 2:
        lines = file_content.split('\n')
    lines = [l for l in lines if len(l)>0 and not (len(l)==1 and l[0].isspace())]
    wav_dir = wav_dir_from_textfile(textfile)
    filter = filters.get(os.path.basename(textfile), '')
    wav_files = get_wav_files(wav_dir, textfile, filter)
    if metadata.get(textfilename,{}).get('wavlist_modification'):
        wav_files = metadata.get(textfilename,{}).get('wavlist_modification')(wav_files)
    skip_lines = metadata.get(textfilename,{}).get('missing_lines',[])
    skip_wavs = metadata.get(textfilename,{}).get('missing_wavs',[])
    if len(wav_files)-len(skip_wavs) != len(lines)-len(skip_lines):
        print("FIRST TRY:", len(wav_files)-len(skip_wavs), len(lines)-len(skip_lines))
        filter = textfilename.replace('.txt','').split('_')[-1]
        wav_files = get_wav_files(wav_dir, textfile, filter)

    if len(wav_files)-len(skip_wavs) != len(lines)-len(skip_lines):
        print(len(wav_files)-len(skip_wavs), len(lines)-len(skip_lines))
        print(textfile)
        print(wav_dir)
        import pdb; pdb.set_trace()
    counter = 0
    for line in lines:
        if counter+1 in skip_lines:
            continue
        prefix, text = prefix_and_text_from_line(line)
        #if not prefix:
            #pair = (wav_files[c], text)
        #else:
            #pair = (find_match(prefix, wav_files), text)
        wav_file = wav_files[counter]
        wav_path = os.path.join(wav_dir,wav_file)
        pair = (wav_path, text)
        pairs.append(pair)
        counter += 1
    return pairs


def main(data_dir, output_file):
    datadict = {}
    for i,f in enumerate(glob(os.path.join(data_dir,'isot_persot/**'), recursive=True)):
         if f.endswith('.wav'):
             datadict[f.split('/')[-1]]=None
    all_pairs = []
    for i,f in enumerate(glob(os.path.join(data_dir,'isot_persot/**/*.txt'), recursive=True)):
        print( i)
        if f.endswith('README.txt') or f.endswith('long_03n_prose_long.txt') or 'notes' in f or 'english' in f or 'long_01m_2013' in f:
            continue
        pairs = handle_textfile2(f)
        all_pairs.extend(pairs)
        for path, text in pairs:
            key = path.split('/')[-1]
            if key in datadict:
                datadict[key] = (path,text)
            else:
                pdb.set_trace()
                pass
    import pdb; pdb.set_trace()
    number_count = 0
    if output_file:
        with open(output_file, 'w') as out_file:
            for i, pair in enumerate(all_pairs):
                line = '{}|{}\n'.format(all_pairs[i][0],all_pairs[i][1].strip().replace('\n', ' '))
                if re.search(r'[0-9]', line.split('|')[1]):
                    number_count += 1
                out_file.write(line)

    print(number_count)
    pass


def num_to_str(line):
    mapping = {
        '21': 'kaksikymmentäyksi',
        '43': 'neljäkymmentäkolme',
        '65': 'kuusikymmentäviisi',
        '87': 'kahdeksankymmentäseitsemän',
        '112': 'satakaksitoista',
        '999': 'yhdeksänsataayhdeksänkymmentäyhdeksän',
        '1000': 'tuhat',
        '1112': 'tuhat satakaksitoista',
        '3456': 'kolmetuhatta neljäsataaviisikymmentäkuusi',
        '7890': 'seitsemäntuhatta kahdeksansataayhdeksänkymmentä',
        '2011': 'kaksituhatta yksitoista',
        '10': 'kymmenen',
        '11': 'yksitoista',
        '56': 'viisikymmentäkuusi',
        '+5': 'plus viisi',
        '+7': 'plus seitsemän',
        '+9': 'plus yhdeksän',
        '-6': 'miinus kuusi',
        '-8': 'miinus kahdeksan',
        '-10': 'miinus kymmenen',
        '+1': 'plus yksi',
        '+2': 'plus kaksi',
        '+3': 'plus kolme',
        '+4': 'plus neljä',
        '+6': 'plus kuusi',
        '+8': 'plus kahdeksan',
        '+10': 'plus kymmenen',
        '+11': 'plus yksitoista',
        '-1': 'miinus yksi',
        '-2': 'miinus kaksi',
        '-3': 'miinus kolme',
        '-4': 'miinus neljä',
        '-5': 'miinus viisi',
        '-7': 'miinus seitsemän',
        '-9': 'miinus yhdeksän',
        '1 + 2 = 3': 'yksi plus kaksi on kolme',
        '4 + 5 = 9': 'neljä plus viisi on yhdeksän',
        '6 * 7 = 42': 'kuusi kertaa seitsemän on neljäkymmentakaksi',
        '81 / 9 = 9': 'kahdeksankymmentäyksi jaettuna yhdeksällä on yhdeksän',
        '3, 2, 1 ja 0.': 'Kolme, kaksi, yksi ja nolla.',
        '0, 1, 2.': 'Nolla, yksi, kaksi.',
        '3, 4, 5.': 'Kolme, neljä, viisi.',
        '6, 7, 8.': 'Kuusi, seitsemän, kahdeksan.',
        '9, 10, 11.': 'Yhdeksän, kymmenen, yksitoista.',
        '1 2 3,  4 5 6.': 'Yksi kaksi kolme, neljä viisi kuusi.',
        '0 5 0,  7 8 9.': 'Nolla viisi nolla, seitsemän kahdekasn yhdeksän.',
        '19, 20, 31.': 'Yhdeksäntoista, kaksikymmentä, kolmekymmentäyksi.',
        '42, 53, 64.': 'Neljäkymmentäkaksi, viisikymmentäkolme, kuusikymmentäneljä.',
        '75, 86, 97.': 'Seitsemänkymmentäviisi, kahdeksankymmentäkuusi, yhdeksänkymmentäseitsemän.',
        '100, 101, 112.': 'Sata, satayksi, satayksitoista.',
        '1000, 1900, 1985.': 'Tuhat, tuhat yhdeksänsataa, tuhat yhdeksänsataakahdeksankymmentäviisi.',
        '2000, 2005, 2011.': 'Kaksituhatta, kaksituhatta viisi, kaksituhatta yksitoista.',
        '2 desiä kevytkermaa, 1 keltuainen, 1 sitruuna, suolaa, valkopippuria.': 'Kaksi desiä kevytkermaa, yksi keltuainen, yksi sitruuna, suolaa, valkopippuria.',
        '1100': 'tuhat sata',
        '1918': 'tuhat yhdeksänsataakahdeksantoista',
        '1950': 'tuhat yhdeksänsataaviisikymmentä',
        '1980': 'tuhat yhdeksänsataakahdeksankyymentä',
        '1995': 'tuhat yhdeksänsataayhdekskänkymmentäviisi',
        '2001': 'kaksituhatta yksi',
        '2010': 'kaksituhatta kymmenen',
        '2211': 'kaksituhatta kaksisataayksitoista',
        '3322': 'kolmetuhatta kolmesataakaksikymmentäkaksi',
        '4433': 'neljätuhatta neljäsataakolmekymmentäkolme',
        '5544': 'viisituhatta viisisataaneljäkymmentäneljä',
        '6666': 'kuusituhatta kuusisataakuusikymmentäkuusi',
        '7766': 'seitsemäntuhatta seitsemänsataakuusikymmentäkuusi',
        '8877': 'kahdeksantuhatta kahdeksansataaseitsemänkymmentäseitsemän',
        '9988': 'yhdeksäntuhatta yhdeksänsataakahdeksankymmentäkahdeksan',
        '100': 'sata',
        '101': 'satayksi',
        '122': 'satakaksikymmentäkaksi',
        '134': 'satakolmekymmentäneljä',
        '200': 'kaksisataa',
        '210': 'kaksisataakymmenen',
        '324': 'kolmesataakaksikymmentäneljä',
        '435': 'neljäsataakolmekymmentäviisi',
        '546': 'viisisataaneljäkymmentäkuusi',
        '657': 'kuusisataaviisikymmentäseitsemän',
        '768': 'seitsemänsataakuusikymmentäkahdeksan',
        '879': 'kahdeksansataaseitsemänkymmentäyhdeksän',
        '900': 'yhdeksänsataa',
        '990': 'yhdeksänsataayhdeksänkymmentä',
        '32': 'kolmekymmentäkaksi',
        '54': 'viisikymmentäneljä',
        '76': 'seitsemänkymmentäkuusi',
        '98': 'yhdeksänkymmentäkahdeksan',
        '10 tuhatta': 'kymmenen tuhatta',
        '11 tuhatta sata yksi': 'yksitoista tuhatta sata yksi',
        '22 tuhatta kaksisataa kaksikymmentä kaksi': 'kaksikymmentäkaksi tuhatta kaksisataa kaksikymmentä kaksi',
        '33 tuhatta kolmesataa kolmekymmentä kolme': 'kolmekymmentäkolme tuhatta kolmesataa kolmekymmentä kolme',
        '44 tuhatta neljäsataa neljäkymmentä neljä': 'neljäkymmentäneljä tuhatta neljäsataa neljäkymmentä neljä',
        '55 tuhatta viisisataa viiisikymmentä viisi': 'viisikymmentäviisi tuhatta viisisataa viiisikymmentä viisi',
        '66 tuhatta kuusisataa kuusikymmentä kuusi': 'kuusikymmentäkuusi tuhatta kuusisataa kuusikymmentä kuusi',
        '77 tuhatta seitsemänsataa seitsemänkymmentä': 'seitsemänkymmentäseitsemän tuhatta seitsemänsataa seitsemänkymmentä',
        '88 tuhatta kahdeksansataa kahdeksankymmentä': 'kahdeksankymmentäkahdeksan tuhatta kahdeksansataa kahdeksankymmentä',
        '99 tuhatta yhdeksänsataa yhdeksänkymmentä': 'yhdeksänkymmentäyhdeksän tuhatta yhdeksänsataa yhdeksänkymmentä',
        '3 miljardia': 'kolme miljardia',
        '5 miljardia': 'viisi miljardia',
        '11 tuhatta kaksisataa kolmekymmentä neljä': 'yksitoista tuhatta kaksisataa kolmekymmentä neljä',
        '56 tuhatta seitsemänsataa kahdeksankymmentä yhdeksän': 'viisikymmentäkuusi tuhatta seitsemänsataa kahdeksankymmentä yhdeksän',
        'Kalastuskunnan vesiin istutettiin siikaa, kuhaa, lahnaa ja harjusta yhteensä 20000:n markan edestä.': 'Kalastuskunnan vesiin istutettiin siikaa, kuhaa, lahnaa ja harjusta yhteensä kahdenkymmenen tuhannen markan edestä.',
        'Suuriin maksuihini tämän kuun 15. päivä minulla ei ole penniäkään.': 'Suuriin maksuihini tämän kuun viidestoista päivä minulla ei ole penniäkään.',
        'Kalastuskunnan vesiin istutettiin siikaa, kuhaa, lahnaa ja harjusta yhteensä 20000 markan edestä.': 'Kalastuskunnan vesiin istutettiin siikaa, kuhaa, lahnaa ja harjusta yhteensä kahdenkymmenen tuhannen markan edestä.',
        'Suuriin maksuihini tämän kuun 15. päivänä minulla ei ole penniäkään.': 'Suuriin maksuihini tämän kuun viidentenätoista päivänä minulla ei ole penniäkään.',
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_directory','-d', required=True, type=str)
    parser.add_argument('--output_file','-o', type=str, default=None)
    arguments = parser.parse_args()

    main(arguments.data_directory, arguments.output_file)
