from global_modules.load_config import Capital, ALL_CONFIGS

CAPITAL: Capital = ALL_CONFIGS['capital']

def calc_credit(S: int, 
                free: int, 
                r_percent: float, T: int):
    """ Высчитываем кредит
        S - сумма кредита
        free - количество ходов без процентов
        r_percent - процентная ставка
        T - срок кредита (в ходах)

        return:
            total - общая сумма к возврату
            pay_per_turn - сумма к возврату за ход
            extra - количество ходов с процентами
    """
    extra = max(0, T - free)
    r = r_percent / 100
    if extra == 0:
        total = S
    else:
        total = S + S * r * extra
    pay_per_turn = total / T
    return int(total), int(pay_per_turn), extra

def get_credit_conditions(reputation: int):
    """ Получаем условия кредита в зависимости от репутации
    """
    conditions = CAPITAL.bank.credit.conditions
    for condition in conditions:
        rep = condition.on_reputation
        if rep.min <= reputation <= rep.max:
            return condition

    raise ValueError("No credit conditions found for the given reputation.")

def check_max_credit_steps(credit_steps: int, 
                           step_now: int, max_steps: int):
    """ Проверяем, что кредит не выйдет за пределы игры
    """

    if step_now + credit_steps > max_steps:
        return False
    return True
