import os
import tqdm

import ljd.rawdump.parser
import ljd.pseudoasm.writer
import ljd.ast.builder
import ljd.ast.validator
import ljd.ast.locals
import ljd.ast.slotworks
import ljd.ast.unwarper
import ljd.ast.mutator
import ljd.lua.writer

SOURCE_DIR = "/home/seraphli/Gitlab/KRF/jit_krf"
OUTPUT_DIR = "./output"


def get_path(path):
    directory = os.path.abspath(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def decompile(file_in, file_out):
    header, prototype = ljd.rawdump.parser.parse(file_in)

    if not prototype:
        return 1

    ast = ljd.ast.builder.build(prototype)
    assert ast is not None
    ljd.ast.validator.validate(ast, warped=True)
    ljd.ast.mutator.pre_pass(ast)
    ljd.ast.locals.mark_locals(ast)
    ljd.ast.slotworks.eliminate_temporary(ast)

    if True:
        ljd.ast.unwarper.unwarp(ast)
        if True:
            ljd.ast.locals.mark_local_definitions(ast)
            ljd.ast.mutator.primary_pass(ast)
            ljd.ast.validator.validate(ast, warped=False)
    with open(file_out, "w") as f:
        ljd.lua.writer.write(f, ast)


def recursive_decompile(source, output):
    error_msg = []
    for root, dirs, files in os.walk(source):
        for f in tqdm.tqdm(files):
            path = os.path.join(root, f)
            if os.path.splitext(path)[1] == ".lua":
                try:
                    decompile(path, os.path.join(
                        get_path(root.replace(source, output)), f))
                except Exception as e:
                    # raise e
                    error_msg.append((path, e))
    for path, e in error_msg:
        print(path, e)


def main():
    file = '/home/seraphli/Gitlab/KRF/jit_krf/screen_map.lua'
    decompile(file, file.replace(SOURCE_DIR, OUTPUT_DIR))
    # recursive_decompile(SOURCE_DIR, get_path(OUTPUT_DIR))


if __name__ == '__main__':
    main()
