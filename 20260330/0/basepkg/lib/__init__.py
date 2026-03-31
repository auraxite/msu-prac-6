def output(*args, **kwargs) -> None:
    """Выводит переданные аргументы в стандартный поток вывода"""
    
    print("".join(x for x in args))