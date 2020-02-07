import copy


class Params:

    def __init__(self):
        self.salary = 0  # To be used for income tax calcuations

        self.house_cost = 0  # market value of the house
        self.initial_cash = 80e3  # initial cash on had that can be put towards downpayment (20% of hosue cost)
        self.down_payment = 0e3  # down payment using initial_cash
        self.monthly_savings = 1000  # amount that can be saved monthly and put towards paying all expenses
        self.property_tax = 4000  # in $/year
        self.bank_rate = 5  # interest rate on case (TFSA or other investments)
        self.income_tax_rate = 0.5  # Tax paid on the profit obtained from rent

        # Mortgage parameters
        self.mortgage_amount = 0
        self.mortgage_rate = 3
        self.mortgage_term = 25
        self.mortgage_extra_payments = 0

        self.heloc_amount = 80e3
        self.heloc_rate = 5
        self.heloc_term = 25
        self.heloc_payments = -1  # -1 pay interest + principle every month, 0 = pay intereest only, deffer principal payment

        # House value and municipal taxes
        self.cost_of_living_increase = 0  # https://www.statista.com/statistics/271247/inflation-rate-in-canada/
        self.property_tax_increase = 0
        self.house_value_increase = 0
        self.house_insurance_per_month = 0
        self.house_utilities = 0  # mostly water, hydro/gas paid by tennants
        self.house_deductibles = 0  # office supplies, car, cell phone, etc

        # Rental parameters
        self.rent = 2000
        self.rent_increase = 0
        self.management_fees = 0
        self.condo_fees = 0

        self.rrsp_account = 100e3  #
        self.rrsp_rate = 5
        self.rrsp_contribution = 100e3 * 0.18 / 12

        self.resp_account = 50e3
        self.resp_rate = 5


class Totals:
    def __init__(self):
        self.property_tax = 0
        self.rent = 0
        self.mortgage_interest = 0
        self.mortgage_payments = 0
        self.heloc_interest = 0
        self.heloc_payments = 0
        self.monthly_tax_deductible_expense = 0
        self.monthly_expense = 0
        self.after_tax_profit = 0
        self.net_worth = 0

    def reset_totals(self):
        self.property_tax = 0
        self.rent = 0
        self.mortgage_interest = 0
        self.mortgage_payments = 0
        self.heloc_interest = 0
        self.heloc_payments = 0
        self.monthly_tax_deductible_expense = 0
        self.monthly_expense = 0
        self.net_worth = 0


def k(val: float) -> float:
    return round(val / 1e3)


def run(obj: object, n: float):
    for i in range(0, n):
        obj.monthly_step()


def calculate_interest(current_balance: float, rate: float) -> float:
    # return [amount going towards servicing interest, amount going towards principal]
    return current_balance * rate


def pmt(principal, rate, num_of_payments):
    # https://en.wikipedia.org/wiki/Mortgage_calculator
    if principal == 0:
        return 0
    y = pow((1 + rate), num_of_payments)
    return principal * (rate * y) / (y - 1)


class Loan:

    def __init__(self, name, amount, annual_interest_rate, term_years, num_of_monthly_payments=1):
        if annual_interest_rate > 1:
            annual_interest_rate = annual_interest_rate / 100

        self.name = name
        self.principal = amount
        self.balance = amount
        self.rate_annual = annual_interest_rate
        self.term = term_years
        self.num_of_months = self.term * 12
        self.num_of_payments = self.num_of_months * num_of_monthly_payments
        self.rate_monthly = self.rate_annual / (12 * num_of_monthly_payments)
        self.payments = pmt(self.principal, self.rate_monthly, self.num_of_payments)
        self.min_payment = calculate_interest(self.principal, self.rate_monthly)

        self.total = {'loan_payment': 0, 'interest_payment': 0, 'num_of_payments': 0}

    def make_extra_payment(self, amount):
        if amount > self.balance:
            amount = self.balance
        self.balance -= amount

    def make_monthly_payment(self, amount=-1):
        interest_payment = calculate_interest(self.balance, self.rate_monthly)

        if amount == -1:
            # If amount is unspecified assume that we pay monthly payment
            payment = self.payments
        elif amount == 0:
            # Paying only intereste and not principal
            payment = 0
        else:
            # paying interest and portion of principal amount
            payment = amount
            if payment < interest_payment:
                print("Cannot make payment less that intereste reate")

        payment_towards_principal = payment - interest_payment

        if payment == 0:
            pass
        else:
            if payment_towards_principal > self.balance:
                payment_towards_principal = self.balance
            self.balance -= payment_towards_principal

        self.total['loan_payment'] += payment_towards_principal
        self.total['interest_payment'] += interest_payment
        self.total['num_of_payments'] += 1
        return interest_payment

    def monthly_step(self, extra_payments=0):
        self.make_monthly_payment()
        self.make_extra_payment(extra_payments)

    def __str__(self):
        return (self.__repr__())

    def __repr__(self):
        return f"{self.name:18} : ${k(self.principal)}k,  {self.term} year ({self.num_of_months} month) @ {self.rate_annual * 100:.1f}% monthly payments ${self.payments:.1f}"

    def summary(self):
        print(
            f"{self.name:18}: total paid ${round(self.total['loan_payment'])} | balance ${k(self.balance)}k | monthly payments: ${self.payments:.2f}  | interest: ${round(self.total['interest_payment'])}k over {self.total['num_of_payments']} payments")


class Investments:

    def __init__(self, name, principal, rate):
        if rate > 1:
            rate = rate / 100

        self.name = name
        self.principal = principal
        self.interest_anual = rate
        self.current_balance = principal

        self.total_interest = 0
        self.total_contributions = 0
        self.monthly_data = []

    def monthly_step(self):
        monthly_interest = self.current_balance * (self.interest_anual / 12)
        self.total_interest += monthly_interest
        self.current_balance += monthly_interest

    def make_deposit(self, amount):
        self.total_contributions += amount
        self.current_balance += amount

    def summary(self):
        print(self.__repr__())

    def __repr__(self):
        return f"{self.name:18}: balance ${self.current_balance:,.2f}k, contributions: {self.total_contributions:,.2f}, total interest {self.total_interest:,.2f}"


class Life:

    def __init__(self, P):

        self.msg = 0

        if P.down_payment > P.initial_cash:
            raise Exception('Downpayment cannot exceede initial cash')

        self.house_cost = P.house_cost
        self.house_value = P.house_cost
        P.mortgage_amount = P.house_cost - (P.down_payment + P.heloc_amount)
        self.mortgage = Loan('Mortgage', P.mortgage_amount, P.mortgage_rate, P.mortgage_term)
        self.heloc = Loan('Heloc', P.heloc_amount, P.heloc_rate, P.heloc_term)

        self.bank_account = Investments('TFSA', P.initial_cash - P.down_payment, P.bank_rate)
        self.rrsp_account = Investments('RRSP', P.rrsp_account, P.rrsp_rate)
        self.resp_account = Investments('RESP', P.resp_account, P.resp_rate)
        self.P = copy.copy(P)
        self.pay_property_tax_monthly = False

        # Internal counters
        self._total_months = 0
        self._current_month = 0
        self._current_year = 0

        self.yearly = Totals()
        self.lifetime = Totals()

        self.log_data = {}
        self.init_log_data()

    def init_log_data(self):
        self.log_data['m'] = []
        self.log_data['y'] = []
        self.log_data['net_cash'] = []
        self.log_data['tax_deductible_expense'] = []
        self.log_data['monthly_expense'] = []
        self.log_data['payment_towards_mortgage'] = []
        self.log_data['mortgage_interest'] = []
        self.log_data['payment_towards_heloc'] = []
        self.log_data['heloc_interest'] = []
        self.log_data['net_worth'] = []

    def get_tax_deductible_monthly_expenses(self):
        # Calculate total expenses
        tax_deductible_monthly_expenses = self.P.house_insurance_per_month + \
                                          self.P.house_utilities + self.P.management_fees + self.P.house_deductibles

        if self.pay_property_tax_monthly:
            tax_deductible_monthly_expenses += (self.P.property_tax / 12.0)

        return tax_deductible_monthly_expenses

    def get_total_monthly_expenses(self):
        return self.get_tax_deductible_monthly_expenses() + \
               self.mortgage.payments + self.heloc.payments

    def monthly_step(self):

        # Collect Rent
        self.yearly.rent += self.P.rent

        # Pay interest on loans
        interest_paid_on_mortgage = self.mortgage.make_monthly_payment()
        payment_towards_mortgage = self.mortgage.payments - interest_paid_on_mortgage
        self.yearly.mortgage_interest += interest_paid_on_mortgage

        # Additional mortgage payments
        self.mortgage.make_extra_payment(self.P.mortgage_extra_payments)

        if self.P.heloc_amount > 0:
            interest_paid_on_heloc = self.heloc.make_monthly_payment(self.P.heloc_payments)
            if self.P.heloc_payments > 0:
                payment_towards_heloc = self.heloc.payments - interest_paid_on_heloc
            else:
                payment_towards_heloc = 0
            self.yearly.heloc_interest += interest_paid_on_heloc
        else:
            interest_paid_on_heloc = 0
            payment_towards_heloc = 0

        # Calculate total expenses
        tax_deductible_expense = interest_paid_on_mortgage + interest_paid_on_heloc + \
                                 self.get_tax_deductible_monthly_expenses()

        self.yearly.monthly_tax_deductible_expense += tax_deductible_expense
        self.lifetime.monthly_tax_deductible_expense += tax_deductible_expense
        self.lifetime.monthly_expense += self.get_total_monthly_expenses()

        total_expense = tax_deductible_expense + payment_towards_mortgage + payment_towards_heloc

        # Calculate cash flow
        net_cash = self.P.rent - total_expense

        self.save_log_data(net_cash, tax_deductible_expense, total_expense, \
                           payment_towards_mortgage, payment_towards_heloc, interest_paid_on_mortgage,
                           interest_paid_on_heloc)

        # Income
        self.bank_account.make_deposit(self.P.monthly_savings)
        self.bank_account.monthly_step()

        if self.P.monthly_savings + net_cash < 0:
            print("Going Broke")

        # self.bank_account.make_deposit(self.P.monthly_savings)
        self.rrsp_account.monthly_step()
        self.rrsp_account.make_deposit(self.P.rrsp_contribution)
        self.resp_account.monthly_step()

        self._total_months += 1
        self._current_month += 1

        if self._current_month == 12:
            self.annual_step()
            self._current_month = 0

    def annual_step(self):
        # total_anual_income - (total_income - total_tax_deductible_expenses) * income_tax_rate

        if self.pay_property_tax_monthly:
            yearly_profit_net = self.yearly.rent - self.yearly.monthly_tax_deductible_expense
        else:
            yearly_profit_net = self.yearly.rent - self.yearly.monthly_tax_deductible_expense - self.P.property_tax
            # yearly_profit_net = self.yearly.rent - self.yearly.mortgage_interest - self.yearly.heloc_interest - self.P.property_tax

        yearly_profit_after_tax = yearly_profit_net * (1 - self.P.income_tax_rate)
        self.bank_account.make_deposit(yearly_profit_after_tax)

        self.lifetime.rent += self.yearly.rent
        self.lifetime.mortgage_interest += self.yearly.mortgage_interest
        self.lifetime.heloc_interest += self.yearly.heloc_interest
        self.lifetime.property_tax += self.P.property_tax
        self.lifetime.after_tax_profit += yearly_profit_after_tax
        self.yearly.reset_totals()

        # Increment costs
        # Account for property tax increase
        self.house_value += self.house_value * (self.P.house_value_increase / 100)
        self.P.property_tax += self.P.property_tax * (self.P.property_tax_increase / 100)
        self.P.house_utilities += self.P.house_utilities * (self.P.cost_of_living_increase / 100)
        self.P.house_insurance_per_month += self.P.house_insurance_per_month * (self.P.cost_of_living_increase / 100)
        self.P.rent += self.P.rent * (self.P.rent_increase / 100)

        self._current_year += 1

    def net_worth(self):
        return (self.bank_account.current_balance + self.house_value) - \
               (self.mortgage.balance + self.heloc.balance)

    def monthly_snapshot(self):

        if self.pay_property_tax_monthly:
            property_tax_monthly = (self.P.property_tax / 12.0)
        else:
            property_tax_monthly = 0

        if self.P.heloc_payments == 0:
            heloc_payments = calculate_interest(self.heloc.balance, self.heloc.rate_monthly)
        else:
            heloc_payments = self.heloc.payments

        print(
            f"Monthly cash flow : ${self.P.rent:4.0f} - $({self.mortgage.payments:4.0f} + {heloc_payments:4.0f} + {self.P.house_insurance_per_month:.0f} + " +
            f"{self.P.house_utilities:4.0f} + {self.P.management_fees:4.0f} + {property_tax_monthly:4.0f}) = " +
            f" ${self.get_total_monthly_expenses():4.0f}, " +
            f"net cash  : ${self.P.rent - self.get_total_monthly_expenses():4.0f}")

    def save_log_data(self, net_cash, tax_deductible_expense, total_expense, payment_towards_mortgage,
                      payment_towards_heloc, mortgage_interest, heloc_interest):
        self.log_data['m'].append(self._total_months)
        self.log_data['y'].append(self._current_year)
        self.log_data['net_cash'].append(net_cash)
        self.log_data['tax_deductible_expense'].append(tax_deductible_expense)
        self.log_data['monthly_expense'].append(total_expense)
        self.log_data['payment_towards_mortgage'].append(payment_towards_mortgage)
        self.log_data['payment_towards_heloc'].append(payment_towards_heloc)
        self.log_data['net_worth'].append(self.net_worth())
        self.log_data['mortgage_interest'].append(mortgage_interest)
        self.log_data['heloc_interest'].append(heloc_interest)

    def summary(self, row=True, header=True, note=''):
        if header:
            print(f"{'':15} |{'Rent':>10} |{'Mort total':>10} |" + \
                  f"{'After Tax':>10} |{'Cash':>10} |{'Net Worth':>10} |" + \
                  f"{'Mort Bal':>10} |{'Heloc Bal':>10} |" + \
                  f"{'Tot Expens':>10} |{'Tax deduc':>10} |" + \
                  f"{'Mt Interes':>10} |{'Hm Interes':>10} |"
                  )

        if row:
            print(
                f"{note:15} |{round(self.lifetime.rent):10,.0f} |{round(self.mortgage.total['loan_payment'] + self.mortgage.total['interest_payment']):10,.0f} |"
                + f"{round(self.lifetime.after_tax_profit):10,.0f} |"
                + f"{round(self.bank_account.current_balance):10,.0f} |"
                + f"{round(self.net_worth()):10,.0f} |"
                + f"{round(self.mortgage.balance):10,.0f} |"
                + f"{round(self.heloc.balance):10,.0f} |"
                + f"{round(self.lifetime.monthly_expense):10,.0f} |"
                + f"{round(self.lifetime.monthly_tax_deductible_expense):10,.0f} |"
                + f"{round(self.lifetime.heloc_interest):10,.0f} |"
                + f"{round(self.lifetime.mortgage_interest):10,.0f} |"
                + f"{round(self.bank_account.current_balance):10,.0f} |"
                )
        else:
            if self._current_year == 0:
                print(f"Initial Conditions")
                self.mortgage.summary()
                if self.P.heloc_amount > 0:
                    self.heloc.summary()
                self.monthly_snapshot()
            else:
                print(f"Totals after {self._current_year} years ({self._total_months} months)")
                print(f"Rent              : ${round(self.lifetime.rent)}")
                print(
                    f"Mortgage total    : ${round(self.mortgage.total['loan_payment'] + self.mortgage.total['interest_payment'])}")
                print(f"Mortgage interest : ${round(self.lifetime.mortgage_interest)}")
                print(f"Monthly Expens    : ${round(self.lifetime.monthly_expense)}")
                print(f"Tax deduct Expens : ${round(self.lifetime.monthly_tax_deductible_expense)}")
                print(f"Property tax      : ${round(self.lifetime.property_tax)}")
                print(f"After tax profit  : ${round(self.lifetime.after_tax_profit)}")
                print(f"House Value       : ${round(self.house_value)}")
                print(f"Net Worth         : ${round(self.net_worth())}")
                self.mortgage.summary()
                if self.P.heloc_amount > 0:
                    self.heloc.summary()

            self.bank_account.summary()

    def run(self, years=0):

        if self.msg > 1:
            self.summary()

        if years == 0:
            years = self.P.mortgage_term

        starting_year = self._current_year
        while (self._current_year - starting_year < years):
            self.monthly_step()

        # return pd.DataFrame(self.log_data)
        return self.log_data


if __name__ == "__main__":
    P = Params()
    L = Life(P)
    L.summary(row=False)
    L.run(20)
    L.summary(header=False)
