from .schemas import FileReadInput, FileReadOutput, FileWriteInput,FileWriteOutput


def read_file(args: FileReadInput) -> FileReadOutput:
    with open(args.path, "r") as f:
        content = f.read()
    return FileReadOutput(content=content)

def write_file(args: FileWriteInput) -> FileWriteOutput:
    with open(args.path, "w") as f:
        f.write(args.content)
    
    return FileWriteOutput(success=True)

