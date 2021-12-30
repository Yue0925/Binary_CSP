import variable


class Constraint(object):
    """ Implementation of a binary constraint object. For the sake of simplicity, all attributes are public.
    """

    def __init__(self, id, var1, var2):
        """Initializes a constraint.

        Args:
            id (int): id of the constraint, should be unique inside a CSP
            var1 (variable.Variable): first variable of the constraint
            var2(variable.Variable): second variable of the constraint
        """
        self.id = id
        self.var1 = var1
        self.var2 = var2

    def __repr__(self):
        return "constraint {0} : ({1}, {2})".format(self.id, self.var1.name, self.var2.name)

    def is_feasible(self, value1: int, value2: int):
        """ Return True if the given assigned values are satisfied by current constraint, False otherwise. """
        raise NotImplemented()

    def reverse(self):
        """Returns a copied constraint where first and second variable roles are inversed

        Returns:
            (Constraint): the reversed constraint
        """
        raise NotImplemented()

    def propagate_assignment(self, assigned_var, assignments, level):
        """After one of its constraints was assigned a value, eliminated infeasible values from the second one's domain

        Args:
            assigned_var (variable.Variable): The variable which was assigned a value during backtracking
            assignments (list): Link between a variable's id and its assigned value
            level (int): Depth on the current branch in backtracking

        Returns:
            (bool): True if the constraint is still feasible after reducing the second variable's domain, False otherwise
        """
        if assigned_var.id == self.var1.id:
            var_to_check = self.var2
        elif assigned_var.id == self.var2.id:
            var_to_check = self.var1
        else:
            raise ValueError("Variable {} not in constraint {} (should be {} or {})".format(
                assigned_var.name, self.id, self.var1.name, self.var2.name
            ))

        if assignments[assigned_var.id] is None:
            raise ValueError("Variable {} should have an assigned value".format(assigned_var.name))

        contradiction = False

        if assignments[var_to_check.id] is None:
            for value in var_to_check.dom(level):

                assignments[var_to_check.id] = value
                feasible = self.is_feasible(assignments[self.var1.id], assignments[self.var2.id])
                assignments[var_to_check.id] = None

                if not feasible:
                    var_to_check.remove_value(value, level + 1)

                    if var_to_check.current_dom_size[level + 1] == 0:
                        contradiction = True
                        break

        return not contradiction


class ConstraintEnum(Constraint):

    def __init__(self, id, var1, var2, feasibility_fun=None):
        """Initializes a constraint.

        Args:
            id (int): id of the constraint, should be unique inside a CSP
            var1 (CSP.Variable): first variable of the constraint
            var2(CSP.Variable): second variable of the constraint
            feasibility_fun (function): function used to generate the set of feasible couples
        """
        super().__init__(id, var1, var2)

        self.feasibleTuples = set()  # l'ensemble couples admissibles
        for a in var1.dom(-1):
            for b in var2.dom(-1):
                if feasibility_fun is None:
                    self.feasibleTuples.add((a, b))
                elif feasibility_fun(var1.id, var2.id, a, b):
                    self.feasibleTuples.add((a, b))

    def is_feasible(self, value1: int, value2: int):
        return (value1, value2) in self.feasibleTuples

    def reverse(self):
        return ConstraintEnum(
            id=-self.id,
            var1=self.var2, var2=self.var1,
            feasibility_fun=lambda x, y, a, b: self.is_feasible(b, a)
        )


class ConstraintLinear(Constraint):

    def __init__(self, id, var1, var2, coef1, coef2, rhs, type):
        """Initializes a constraint.

        Args:
            id (int): id of the constraint, should be unique inside a CSP
            var1 (CSP.Variable): first variable of the constraint
            var2(CSP.Variable): second variable of the constraint
            coef1(float): Coefficient associated with the first variable
            coef2(float): Coefficient associated with the second variable
            rhs(float): right-hand side
            type (str): type of linear constraint.
                Can be "g" (greater), "geq" (greater or equal), "l" (lower), "leq" (lower or equal), "eq" (equal)
                or "neq" (not equal).
        """
        super().__init__(id, var1, var2)

        self.coef1 = coef1
        self.coef2 = coef2
        self.rhs = rhs

        self.type = type
        if type == "eq":
            self.check_function = lambda x, y: x == y
        elif type == "g":
            self.check_function = lambda x, y: x > y
        elif type == "geq":
            self.check_function = lambda x, y: x >= y
        elif type == "l":
            self.check_function = lambda x, y: x < y
        elif type == "leq":
            self.check_function = lambda x, y: x <= y
        elif type == "neq":
            self.check_function = lambda x, y: x != y

    def is_feasible(self, value1: int, value2: int):
        return self.check_function(self.coef1 * value1 + self.coef2 * value2, self.rhs)

    def reverse(self):
        return ConstraintLinear(
            id=-self.id,
            var1=self.var2, var2=self.var1,
            coef1=self.coef2, coef2=self.coef1, rhs=self.rhs,
            type=self.type
        )

    def propagate_assignment(self, assigned_var, assignments, level):
        if assignments[assigned_var.id] is None:
            raise ValueError("Variable {} should have an assigned value".format(assigned_var.name))

        if assigned_var.id == self.var1.id:
            updated_rhs = (self.rhs - self.coef1 * assignments[assigned_var.id]) / self.coef2  # TODO: gerer le cas coef=0 ailleurs
            var_to_check = self.var2

        elif assigned_var.id == self.var2.id:
            updated_rhs = (self.rhs - self.coef2 * assignments[assigned_var.id]) / self.coef1  # TODO: gerer le cas coef=0 ailleurs
            var_to_check = self.var1

        else:
            raise ValueError("Variable {} not in constraint {} (should be {} or {})".format(
                assigned_var.name, self.id, self.var1.name, self.var2.name
            ))

        contradiction = False

        if assignments[var_to_check.id] is None:
            for value in var_to_check.dom(level):

                if not self.check_function(value, updated_rhs):
                    var_to_check.remove_value(value, level + 1)

                    if var_to_check.current_dom_size[level + 1] == 0:
                        contradiction = True
                        break

        return not contradiction