(function (root) {
    'use strict';

    const keyGroups = Object.freeze({
        2: 'abc',
        3: 'def',
        4: 'ghi',
        5: 'jkl',
        6: 'mno',
        7: 'pqrs',
        8: 'tuv',
        9: 'wxyz'
    });

    const syllables = new Set((
        'a ai an ang ao ba bai ban bang bao bei ben beng bi bian biang biao bie bin bing bo bu ' +
        'ca cai can cang cao ce cei cen ceng cha chai chan chang chao che chen cheng chi chong chou chu chua chuai chuan chuang chui chun chuo ' +
        'ci cong cou cu cuan cui cun cuo da dai dan dang dao de dei den deng di dia dian diao die din ding diu dong dou du duan dui dun duo ' +
        'e eh ei en eng er fa fan fang fei fen feng fiao fo fong fou fu ga gai gan gang gao ge gei gen geng gong gou gu gua guai guan guang gui gun guo ' +
        'ha hai han hang hao he hei hen heng hong hou hu hua huai huan huang hui hun huo ' +
        'ji jia jian jiang jiao jie jin jing jiong jiu ju juan jue jun ka kai kan kang kao ke kei ken keng kong kou ku kua kuai kuan kuang kui kun kuo ' +
        'la lai lan lang lao le lei leng li lia lian liang liao lie lin ling liu lo long lou lu luan lun luo lv lvan lve ' +
        'ma mai man mang mao me mei men meng mi mian miao mie min ming miu mo mou mu ' +
        'na nai nan nang nao ne nei nen neng ni nia nian niang niao nie nin ning niu nong nou nu nuan nun nuo nv nve ' +
        'o ou pa pai pan pang pao pei pen peng pi pia pian piao pie pin ping po pou pu ' +
        'qi qia qian qiang qiao qie qin qing qiong qiu qu quan que qun ' +
        'ran rang rao re ren reng ri rong rou ru rua ruan rui run ruo ' +
        'sa sai san sang sao se sei sen seng sha shai shan shang shao she shei shen sheng shi shou shu shua shuai shuan shuang shui shun shuo ' +
        'si song sou su suan sui sun suo ta tai tan tang tao te tei teng ti tian tiao tie ting tong tou tu tuan tui tun tuo ' +
        'wa wai wan wang wei wen weng wo wong wu xi xia xian xiang xiao xie xin xing xiong xiu xu xuan xue xun ' +
        'ya yai yan yang yao ye yi yin ying yo yong you yu yuan yue yun ' +
        'za zai zan zang zao ze zei zen zeng zha zhai zhan zhang zhao zhe zhei zhen zheng zhi zhong zhou zhu zhua zhuai zhuan zhuang zhui zhun zhuo ' +
        'zi zong zou zu zuan zui zun zuo'
    ).trim().split(/\s+/));

    const commonOrder = (
        'de yi shi zhi le zai ren you wo ta zhe ge men zhong lai shang da wei he ni hao bu hui ' +
        'jiang shuo yao dao jiu ye neng mei kan hen qu dou gei hai ba rang xia guo xiang zhen ' +
        'li ming tian xian sheng dian hua jia xin qing dui qi zi er hou qian kai dan yu ' +
        'cheng chang wu tong nian jin zuo mei xue wen gan chu bie'
    ).trim().split(/\s+/);
    const commonRank = new Map(commonOrder.map((value, index) => [value, index]));
    const initialOrder = 'nhwszyjxqdlgbmrtfcpkaeouv';
    const initialRank = new Map([...initialOrder].map((value, index) => [value, index]));

    function digitsFor(text) {
        let result = '';
        for (const letter of text) {
            const digit = Object.keys(keyGroups).find(key => keyGroups[key].includes(letter));
            if (!digit) return '';
            result += digit;
        }
        return result;
    }

    const prefixIndex = new Map();
    for (const syllable of syllables) {
        const digits = digitsFor(syllable);
        const syllableScore = commonRank.get(syllable) ?? (1000 + syllable.length * 10);

        for (let length = 1; length <= syllable.length; length++) {
            const digitPrefix = digits.slice(0, length);
            const letterPrefix = syllable.slice(0, length);
            let entries = prefixIndex.get(digitPrefix);

            if (!entries) {
                entries = new Map();
                prefixIndex.set(digitPrefix, entries);
            }

            const existing = entries.get(letterPrefix);
            if (!existing || syllableScore < existing.score) {
                entries.set(letterPrefix, {
                    text: letterPrefix,
                    complete: syllables.has(letterPrefix),
                    score: syllableScore
                });
            } else if (syllables.has(letterPrefix)) {
                existing.complete = true;
            }
        }
    }

    function candidatesForDigits(digits, preferredPrefix = '') {
        if (!/^[2-9]{1,6}$/.test(digits)) return [];
        const entries = prefixIndex.get(digits);
        if (!entries) return [];

        return [...entries.values()]
            .map(entry => ({ ...entry }))
            .sort((left, right) => {
                const leftPreferred = preferredPrefix && left.text.startsWith(preferredPrefix) ? 0 : 1;
                const rightPreferred = preferredPrefix && right.text.startsWith(preferredPrefix) ? 0 : 1;
                if (leftPreferred !== rightPreferred) return leftPreferred - rightPreferred;

                const leftExact = commonRank.get(left.text) ?? Number.MAX_SAFE_INTEGER;
                const rightExact = commonRank.get(right.text) ?? Number.MAX_SAFE_INTEGER;
                if (leftExact !== rightExact) return leftExact - rightExact;

                const leftInitial = initialRank.get(left.text[0]) ?? 99;
                const rightInitial = initialRank.get(right.text[0]) ?? 99;
                if (leftInitial !== rightInitial) return leftInitial - rightInitial;

                if (left.score !== right.score) return left.score - right.score;

                return left.text.localeCompare(right.text);
            });
    }

    root.T9Pinyin = Object.freeze({
        candidatesForDigits,
        digitsFor,
        isComplete: value => syllables.has(value),
        lettersForDigit: digit => keyGroups[digit] || ''
    });
})(typeof window !== 'undefined' ? window : globalThis);
