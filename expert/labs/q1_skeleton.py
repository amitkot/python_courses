# ========== Q1: Properties ==========
class PersonV1:
    """Implement name/age/email via properties with validation.

    - name: non-empty str (after strip)
    - age: int >= 0 (bool is invalid)
    - email: contains '@'; normalize on set with strip().lower()
    """

    def __init__(self, name: str, age: int, email: str) -> None:
        # you may initialize backing attributes here
        self._name: str
        self._age: int
        self._email: str
        # TODO: assign via properties below
        raise NotImplementedError

    @property
    def name(self) -> str:
        # TODO
        raise NotImplementedError

    @name.setter
    def name(self, value: str) -> None:
        # TODO: validate non-empty str
        raise NotImplementedError

    @property
    def age(self) -> int:
        # TODO
        raise NotImplementedError

    @age.setter
    def age(self, value: int) -> None:
        # TODO: int >= 0 and not bool
        raise NotImplementedError

    @property
    def email(self) -> str:
        # TODO
        raise NotImplementedError

    @email.setter
    def email(self, value: str) -> None:
        # TODO: contains '@' then normalize: strip().lower()
        raise NotImplementedError


# Helpers you can reuse in properties and descriptor


def ensure_str_non_empty(v: Any) -> str:
    if not isinstance(v, str) or not v.strip():
        raise TypeError("must be a non-empty str")
    return v


def ensure_int_ge0(v: Any) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise TypeError("must be int >= 0")
    return v


def normalize_email(v: Any) -> str:
    if not isinstance(v, str):
        raise TypeError("email must be str")
    return v.strip().lower()


def ensure_email(v: str) -> str:
    if "@" not in v:
        raise TypeError("email must contain '@'")
    return v


if __name__ == "__main__":
    print("Mini-Lab: run tests after you implement Q1/Q2.\n")

    # --- Q1 checks (uncomment after you implement PersonV1) ---
    # pv1 = PersonV1("Amit", 44, "  AMIT@EXAMPLE.COM ")
    # assert pv1.name == "Amit"
    # assert pv1.age == 44
    # assert pv1.email == "amit@example.com"
    # print("Q1 OK")
