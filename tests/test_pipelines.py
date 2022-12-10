class FixedPipeline:
    def __init__(self):
        third = print_paras()
        third.send(None)
        second = chunk_to_words(third)
        second.send(None)

        self.first = get_paras(second)
        self.first.send(None)


    def process(self, input: Iterable):
        for line in input:
            self.first.send(line.rstrip())


