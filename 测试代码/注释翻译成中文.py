import tokenize
from deep_translator import GoogleTranslator  # 替换库


def translate_python_file(input_file, output_file):
    # 初始化同步翻译器
    translator = GoogleTranslator(source='auto', target='zh-CN')

    with open(input_file, 'rb') as f:
        tokens = list(tokenize.tokenize(f.readline))

    new_tokens = []

    for tok in tokens:
        token_type = tok.type
        token_string = tok.string

        # 处理 # 注释
        if token_type == tokenize.COMMENT:
            content = token_string.lstrip('#').strip()
            if content:
                try:
                    # 这里的 translate 是同步的，不会报错
                    translated = translator.translate(content)
                    new_tokens.append((token_type, f"# {translated}"))
                except Exception:
                    new_tokens.append((token_type, token_string))
            else:
                new_tokens.append((token_type, token_string))

        # 处理 """ 或 ''' 文档字符串
        elif token_type == tokenize.STRING and (token_string.startswith('"""') or token_string.startswith("'''")):
            quote_type = token_string[:3]
            content = token_string[3:-3].strip()

            if content:
                try:
                    translated = translator.translate(content)
                    new_tokens.append((token_type, f"{quote_type}\n{translated}\n{quote_type}"))
                except Exception:
                    new_tokens.append((token_type, token_string))
            else:
                new_tokens.append((token_type, token_string))
        else:
            new_tokens.append((token_type, token_string))

    # 还原代码
    result = tokenize.untokenize(new_tokens)
    if isinstance(result, bytes):
        result = result.decode('utf-8')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"翻译完成！已存至: {output_file}")


# 运行
translate_python_file('../spcm_dir/examples/03_dds/01_dds_single_static_carrier.py', 'output_cn.py')