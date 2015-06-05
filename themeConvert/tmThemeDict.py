__author__ = 'ethan'


def merge_lists(list1, list2):
    new_list1 = list1
    # for i in list1:
    #   if i not in list2:
    #        new_list1.append(i)

    for x in list2:
        if x not in list1:
            new_list1.append(x)

    return new_list1

s_d = {'comment': ['comment', 'markup.comment', 'style.comment'],
       'meta.property-name.css': [],
       'constant.other.color': ['keyword.control'],
       'support.type': [],
       'support.constant.property-value.css': [],
       'constant.language': ['constant.numeric.keyword'],
       'constant.other.color.rgb-value.css': [],
       'entity.name.function': [],
       'constant.character.entity': [],
       'storage': [],
       'entity.other.attribute-name.id.css': [],
       'invalid': [],
       'entity.other.attribute-name': ['markup.inline.cdata', 'markup.tag'],
       'keyword.other.unit': [],
       'entity.other.attribute-name.html': ['markup.tag.attribute.name'],
       'meta.selector.css': [],
       'string': [],
       'variable.other': [],
       'support.class.js': [],
       'constant.other': [],
       'entity.other.inherited-class': [],
       'punctuation.section.embedded': [],
       'entity.name.tag.css': [],
       'entity.name.class': [],
       'constant.numeric': [],
       'entity.name.tag': ['markup.inline.cdata', 'markup.tag'],
       'support.constant.property-value': ['keyword.control'],
       'support.constant': [],
       'constant.character': [],
       'keyword': ['keyword.control'],
       'settings': ['meta.default'],
       'variable.language': [],
       'support.other.variable': [],
       'variable.parameter': [],
       'punctuation.definition.tag': ['markup.inline.cdata', 'markup.tag'],
       'support.function': [],
       'keyword.operator': [],
       'entity.other.attribute-name.class.css': [],
       'support.class': []}

s_d2 = {'comment': ['comment', 'markup.comment', 'style.comment'],
        'invalid.deprecated': [],
        'constant': [],
        'entity': [],
        'text.tex.latex support.function': ['keyword', 'keyword.control', 'keyword.type'],
        'keyword.type.variant': [],
        'string constant.other.placeholder': [],
        'source.ocaml keyword.operator.symbol.prefix.floating-point': [],
        'support': ['support'],
        'storage': ['keyword', 'keyword.control', 'keyword.type'],
        'meta.tag entity': [],
        'entity.name.section': [],
        'text.tex.latex meta.function.environment': [],
        'source.ocaml keyword.operator.symbol.prefix': ['support'],
        'invalid.illegal': [],
        'meta.function-call.py': [],
        'text.tex.latex meta.function.environment meta.function.environment': [],
        'source.plist string.unquoted': [],
        'source.ocaml keyword.operator.symbol': [],
        'string': ['markup.tag.attribute.value', 'meta.link', 'string', 'style.value.string'],
        'source.plist keyword.operator': [],
        'entity.other.inherited-class': [],
        'meta.tag': [],
        'variable': [],
        'source.ocaml keyword.operator.symbol.infix.floating-point': [],
        'source.ocaml keyword.operator.symbol.infix': ['support'],
        'meta.verbatim': ['markup.tag.attribute.value', 'meta.link', 'string', 'style.value.string'],
        'keyword': ['keyword', 'keyword.control', 'keyword.type'],
        'settings': [],
        'source.ocaml constant.numeric.floating-point': []}

s_d3 = {'comment': ['comment', 'markup.comment', 'style.comment'],
        'constant': [],
        'constant.character': [],
        'constant.character.entity': [],
        'constant.language': ['constant.numeric.keyword'],
        'constant.numeric': [],
        'constant.other': [],
        'constant.other.color': ['keyword.control'],
        'constant.other.color.rgb-value.css': [],
        'entity': [],
        'entity.name.class': [],
        'entity.name.function': [],
        'entity.name.section': [],
        'entity.name.tag': ['markup.inline.cdata', 'markup.tag'],
        'entity.name.tag.css': [],
        'entity.other.attribute-name': ['markup.inline.cdata', 'markup.tag'],
        'entity.other.attribute-name.class.css': [],
        'entity.other.attribute-name.html': ['markup.tag.attribute.name'],
        'entity.other.attribute-name.id.css': [],
        'entity.other.inherited-class': [],
        'invalid': [],
        'invalid.deprecated': [],
        'invalid.illegal': [],
        'keyword': ['keyword.control', 'keyword', 'keyword.type'],
        'keyword.operator': [],
        'keyword.other.unit': [],
        'keyword.type.variant': [],
        'meta.function-call.py': [],
        'meta.property-name.css': [],
        'meta.selector.css': [],
        'meta.tag': [],
        'meta.tag entity': [],
        'meta.verbatim': ['markup.tag.attribute.value', 'meta.link', 'string', 'style.value.string'],
        'punctuation.definition.tag': ['markup.inline.cdata', 'markup.tag'],
        'punctuation.section.embedded': [],
        'settings': ['meta.default'],
        'source.ocaml constant.numeric.floating-point': [],
        'source.ocaml keyword.operator.symbol': [],
        'source.ocaml keyword.operator.symbol.infix': ['support'],
        'source.ocaml keyword.operator.symbol.infix.floating-point': [],
        'source.ocaml keyword.operator.symbol.prefix': ['support'],
        'source.ocaml keyword.operator.symbol.prefix.floating-point': [],
        'source.plist keyword.operator': [],
        'source.plist string.unquoted': [],
        'storage': ['keyword', 'keyword.control', 'keyword.type'],
        'string': ['markup.tag.attribute.value', 'meta.link', 'string', 'style.value.string'],
        'string constant.other.placeholder': [],
        'support': ['support'],
        'support.class': [],
        'support.class.js': [],
        'support.constant': [],
        'support.constant.property-value': ['keyword.control'],
        'support.constant.property-value.css': [],
        'support.function': [],
        'support.other.variable': [],
        'support.type': [],
        'text.tex.latex meta.function.environment': [],
        'text.tex.latex meta.function.environment meta.function.environment': [],
        'text.tex.latex support.function': ['keyword', 'keyword.control', 'keyword.type'],
        'variable': [],
        'variable.language': [],
        'variable.other': [],
        'variable.parameter': []}


if __name__ == '__main__':
    s_d_merged = dict()
    both_keys = merge_lists(s_d.keys(), s_d2.keys())
    for m_k in both_keys:
        v1 = []
        v2 = []
        if m_k in s_d.keys():
            v1 = s_d[m_k]
        if m_k in s_d2.keys():
            v2 = s_d2[m_k]
        n_v = merge_lists(v1, v2)
        s_d_merged[m_k] = n_v

    for k in sorted(s_d_merged.keys()):
        print "\'" + k + "\':", str(s_d_merged[k]) + ","
    #print s_d_merged