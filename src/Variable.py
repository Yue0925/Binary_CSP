import numbers
import Constraint


class Variable(object):
    """ Implementation of a variable object. For the sake of simplicity, all attributes are public.
    """

    def __init__(self, id: int, name: str, domMin: int, domMax: int):  # , domFun):
        """ Initialize a variable."""
        self.id = id
        self.name = name  # facultatif

        self.domMin = domMin
        self.domMax = domMax
        self._dom = list(range(domMin, domMax + 1))  # domaine énumérée, l'ens élément finis
        self.dom_size = len(self._dom)
        # self.domFun = domFun  # domaine defini par une fonction
        self.level = -1
        self.current_dom_size = None
        self.associated_constrs = None

    def __repr__(self):
        return "variable {}".format(self.name)

    def dom(self, level: int = -1):
        """Return the domain of the variable for the specified depth level during backtrack search

        Args:
            level (int): Depth level (on the current branch). If level=-1, returns the initial domain of the variable.

        Returns:
            (list): list of all remaining possible values at given level
        """
        if level == -1:
            return self._dom[:]
        return self._dom[:self.current_dom_size[level]]

    def remove_value(self, value:int, level:int):
        """ Remove the given value from the domain at actual level of research tree"""
        last = self.current_dom_size[level] - 1
        to_remove = -1
        for i in range(last + 1):
            if self._dom[i] == value:
                to_remove = i
                break

        if to_remove == -1:
            raise ValueError("Value {} not found in variable {}'s domain at level {}".format(value, self.name, level))
        self._dom[to_remove], self._dom[last] = self._dom[last], self._dom[to_remove]
        self.current_dom_size[level] -= 1

    def remove_all_values_except(self, value: int, level: int):
        last = self.current_dom_size[level] - 1
        to_keep = -1
        for i in range(last + 1):
            if self._dom[i] == value:
                to_keep = i
                break

        if to_keep == -1:
            raise ValueError("Value {} not found in variable {}'s domain at level {}".format(value, self.name, level))
        self._dom[to_keep], self._dom[0] = self._dom[0], self._dom[to_keep]
        self.current_dom_size[level] = 1

    def __add__(self, other):
        return LinearExpr(var1=self, coef1=1) + other

    def __mul__(self, other):
        return LinearExpr(var1=self, coef1=1) * other

    def __sub__(self, other):
        return LinearExpr(var1=self, coef1=1) - other

    def __eq__(self, other):
        return LinearExpr(var1=self, coef1=1) == other

    def __ne__(self, other):
        return LinearExpr(var1=self, coef1=1) != other

    def __lt__(self, other):
        return LinearExpr(var1=self, coef1=1) < other

    def __le__(self, other):
        return LinearExpr(var1=self, coef1=1) <= other

    def __gt__(self, other):
        return LinearExpr(var1=self, coef1=1) > other

    def __ge__(self, other):
        return LinearExpr(var1=self, coef1=1) >= other


class LinearExpr(object):

    def __init__(self, var1=None, var2=None, coef1=0., coef2=0., constant=0.):
        self.var1 = var1
        self.coef1 = coef1
        self.var2 = var2
        self.coef2 = coef2
        self.constant = constant

    def __repr__(self):
        if self.var1 is None and self.var2 is None:
            return str(self.constant)
        if self.var1 is None:
            return "{} * {} + {}".format(self.coef2, self.var2.name, self.constant)
        if self.var2 is None:
            return "{} * {} + {}".format(self.coef1, self.var1.name, self.constant)
        else:
            return "{} * {} + {} * {} + {}".format(self.coef1, self.var1.name, self.coef2, self.var2.name, self.constant)

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return LinearExpr(self.var1, self.var2, self.coef1, self.coef2, self.constant + other)

        elif isinstance(other, Variable):
            if self.var1.id == other.id:
                return LinearExpr(self.var1, self.var2, self.coef1 + 1, self.coef2, self.constant)
            elif self.var2.id == other.id:
                return LinearExpr(self.var1, self.var2, self.coef1, self.coef2 + 1, self.constant)
            elif self.var1 is None:
                return LinearExpr(other, self.var2, 1, self.coef2, self.constant)
            elif self.var2 is None:
                return LinearExpr(self.var1, other, self.coef1, 1, self.constant)
            else:
                raise ValueError("Trying to add a variable to an expression already containing 2")

        elif isinstance(other, LinearExpr):
            if self.var1 is None and self.var2 is None:
                return other + self.constant
            elif other.var1 is None and other.var2 is None:
                return self + other.constant
            elif self.var1 is None and (other.var2 is None or self.var2.id == other.var2.id):
                return LinearExpr(other.var1, self.var2, other.coef1, self.coef2 + other.coef2, self.constant + other.constant)
            elif self.var1 is None and (other.var1 is None or self.var2.id == other.var1.id):
                return LinearExpr(other.var2, self.var2, other.coef2, self.coef2 + other.coef1, self.constant + other.constant)
            elif self.var2 is None and (other.var1 is None or self.var1.id == other.var1.id):
                return LinearExpr(self.var1, other.var2, self.coef1 + other.coef1, other.coef2, self.constant + other.constant)
            elif self.var2 is None and (other.var2 is None or self.var1.id == other.var2.id):
                return LinearExpr(self.var1, other.var1, self.coef1 + other.coef2, other.coef1, self.constant + other.constant)
            if self.var1.id == other.var1.id and self.var2.id == other.var2.id:
                return LinearExpr(self.var1, self.var2, self.coef1 + other.coef1, self.coef2 + other.coef2, self.constant + other.constant)
            elif self.var2.id == other.var1.id and self.var1.id == other.var2.id:
                return LinearExpr(self.var1, self.var2, self.coef1 + other.coef2, self.coef2 + other.coef1, self.constant + other.constant)
            else:
                raise ValueError("Trying to add a variable to an expression already containing 2")

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return LinearExpr(self.var1, self.var2, self.coef1 * other, self.coef2 * other, self.constant * other)

    def __sub__(self, other):
        return self + other * -1

    def __eq__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="eq"
        )

    def __ne__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="neq"
        )

    def __lt__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="l"
        )

    def __le__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="leq"
        )

    def __gt__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="g"
        )

    def __ge__(self, other):
        expr = self - other
        return Constraint.ConstraintLinear(
            id=-1,
            var1=expr.var1, var2=expr.var2,
            coef1=expr.coef1, coef2=expr.coef2, rhs=-expr.constant,
            type="geq"
        )
