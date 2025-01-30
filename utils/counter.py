from typing import Any, Optional, Union, Tuple, List, Dict
import time
import ast
import math
import numpy
import operator
import sqlite3
from word2number import w2n

class CounterUtils:
    """Safe mathematical expression evaluator."""
    
    # Supported operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Supported math functions with their safe implementations
    SAFE_FUNCTIONS = {
        # Math module constants
        'pi': lambda: math.pi,
        'e': lambda: math.e,
        'tau': lambda: math.tau,
        'inf': lambda: math.inf,
        'nan': lambda: math.nan,

        # Basic math functions
        'ceil': math.ceil,
        'floor': math.floor,
        'abs': abs,
        'fabs': math.fabs,
        'sqrt': math.sqrt,
        'pow': math.pow,
        
        # Advanced math functions
        'factorial': math.factorial,
        'gcd': math.gcd,
        'lcm': math.lcm,
        'fmod': math.fmod,
        'modf': math.modf,
        'copysign': math.copysign,
        'isfinite': math.isfinite,
        'isinf': math.isinf,
        'isnan': math.isnan,
        'isqrt': math.isqrt,
        'ldexp': math.ldexp,
        'frexp': math.frexp,
        'fsum': math.fsum,
        'prod': math.prod,
        'perm': math.perm,
        'comb': math.comb,
        'remainder': math.remainder,
        
        # Exponential and logarithmic functions
        'exp': math.exp,
        'expm1': math.expm1,
        'log': math.log,
        'log1p': math.log1p,
        'log2': math.log2,
        'log10': math.log10,
        
        # Trigonometric functions
        'sin': lambda x: math.sin(math.radians(x)),
        'cos': lambda x: math.cos(math.radians(x)),
        'tan': lambda x: math.tan(math.radians(x)),
        'asin': lambda x: math.degrees(math.asin(x)),
        'acos': lambda x: math.degrees(math.acos(x)),
        'atan': lambda x: math.degrees(math.atan(x)),
        'atan2': math.atan2,
        'dist': math.dist,
        'hypot': math.hypot,
        'degrees': math.degrees,
        'radians': math.radians,
        
        # Hyperbolic functions
        'sinh': lambda x: math.sinh(math.radians(x)),
        'cosh': lambda x: math.cosh(math.radians(x)),
        'tanh': lambda x: math.tanh(math.radians(x)),
        'asinh': lambda x: math.degrees(math.asinh(x)),
        'acosh': lambda x: math.degrees(math.acosh(x)),
        'atanh': lambda x: math.degrees(math.atanh(x)),

        # Special functions
        'erf': math.erf,
        'erfc': math.erfc,
        'gamma': math.gamma,
        'lgamma': math.lgamma,

        # NumPy trigonometric functions
        'numpysin':lambda x: numpy.sin(math.radians(x)),
        'numpycos': lambda x: numpy.cos(math.radians(x)),
        'numpytan': lambda x: numpy.tan(math.radians(x)),
        'numpyarcsin': lambda x: math.degrees(numpy.arcsin(x)),
        'numpyarccos': lambda x: math.degrees(numpy.arccos(x)),
        'numpyarctan': lambda x: math.degrees(numpy.arctan(x)),
        'numpyhypot': numpy.hypot,
        'numpyarctan2': numpy.arctan2,
        'numpydegrees': numpy.degrees,
        'numpyradians': numpy.radians,
        'numpyunwrap': numpy.unwrap,
        'numpydeg2rad': numpy.deg2rad,
        'numpyrad2deg': numpy.rad2deg,
        
        # NumPy hyperbolic functions
        'numpysinh': lambda x: numpy.sin(math.radians(x)),
        'numpycosh':lambda x: numpy.cos(math.radians(x)),
        'numpytanh': lambda x: numpy.tan(math.radians(x)),
        'numpyarcsinh': lambda x: math.degrees(numpy.arcsinh(x)),
        'numpyarccosh': lambda x: math.degrees(numpy.arccosh(x)),
        'numpyarctanh': lambda x: math.degrees(numpy.arctanh(x)),
        
        # NumPy rounding functions
        'numpyaround': numpy.around,
        'numpyround_': numpy.round,
        'numpyrint': numpy.rint,
        'numpyfix': numpy.fix,
        'numpyfloor': numpy.floor,
        'numpyceil': numpy.ceil,
        'numpytrunc': numpy.trunc,
        
        # NumPy sum/product functions
        'numpyprod': numpy.prod,
        'numpysum': numpy.sum,
        'numpynanprod': numpy.nanprod,
        'numpynansum': numpy.nansum,
        'numpycumprod': numpy.cumprod,
        'numpycumsum': numpy.cumsum,
        'numpynancumprod': numpy.nancumprod,
        'numpynancumsum': numpy.nancumsum,
        
        # NumPy arithmetic functions
        'numpyadd': numpy.add,
        'numpysubtract': numpy.subtract,
        'numpymultiply': numpy.multiply,
        'numpydivide': numpy.divide,
        'numpypower': numpy.power,
        'numpymod': numpy.mod,
        'numpyfmod': numpy.fmod,
        'numpyremainder': numpy.remainder,
        'numpydivmod': numpy.divmod,
        
        # NumPy exponential/logarithmic functions
        'numpyexp': numpy.exp,
        'numpyexpm1': numpy.expm1,
        'numpyexp2': numpy.exp2,
        'numpylog': numpy.log,
        'numpylog10': numpy.log10,
        'numpylog2': numpy.log2,
        'numpylog1p': numpy.log1p,
        'numpylogaddexp': numpy.logaddexp,
        'numpylogaddexp2': numpy.logaddexp2,
        
        # NumPy miscellaneous functions
        'numpysqrt': numpy.sqrt,
        'numpycbrt': numpy.cbrt,
        'numpysquare': numpy.square,
        'numpyabsolute': numpy.absolute,
        'numpyfabs': numpy.fabs,
        'numpysign': numpy.sign,
        'numpyreciprocal': numpy.reciprocal,
        'numpypositive': numpy.positive,
        'numpynegative': numpy.negative,
        'numpyreal': numpy.real,
        'numpyimag': numpy.imag,
        'numpyconj': numpy.conj,
        'numpyconjugate': numpy.conjugate,
        
        # NumPy statistical functions
        'numpymaximum': numpy.maximum,
        'numpyfmax': numpy.fmax,
        'numpyamax': numpy.amax,
        'numpynanmax': numpy.nanmax,
        'numpyfmin': numpy.fmin,
        'numpyamin': numpy.amin,
        'numpynanmin': numpy.nanmin,
        
        # NumPy signal processing
        'numpyconvolve': numpy.convolve,
        'numpyinterp': numpy.interp,
        
        # NumPy complex number operations
        'numpyangle': numpy.angle,
        'numpyreal_if_close': numpy.real_if_close,
        
        # NumPy floating point routines
        'numpysignbit': numpy.signbit,
        'numpycopysign': numpy.copysign,
        'numpyfrexp': numpy.frexp,
        'numpyldexp': numpy.ldexp,
        'numpynextafter': numpy.nextafter,
        'numpyspacing': numpy.spacing,
        
        # NumPy comparison functions
        'numpyclip': numpy.clip,
        'numpyheaviside': numpy.heaviside,
    }

    def __init__(self, db_path: str = 'counting.db', max_digits: int = 20):
        self.db_path = db_path
        self.max_digits = max_digits
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            
            # Create server settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server (
                    serverID TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 1,
                    last_counter TEXT,
                    high_score INTEGER NOT NULL DEFAULT 0,
                    fails INTEGER NOT NULL DEFAULT 0,
                    counts INTEGER NOT NULL DEFAULT 0,
                    primes INTEGER NOT NULL DEFAULT 0
                )
            ''')

            # Create user stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mathematicians (
                    ID TEXT,
                    serverID TEXT,
                    fails INTEGER DEFAULT 0,
                    counts INTEGER DEFAULT 0,
                    high_score INTEGER DEFAULT 0,
                    last_fail INTEGER DEFAULT 0,
                    last_fail_date TEXT,
                    last_count INTEGER DEFAULT 0,
                    delta_fail INTEGER DEFAULT 0,
                    primes INTEGER DEFAULT 0,
                    PRIMARY KEY (ID, serverID)
                )
            ''')
            db.commit()

    def _eval_node(self, node: ast.AST) -> Any:
        """Safely evaluate an AST node."""
        
        # Numeric values
        if isinstance(node, ast.Num):
            return node.n

        # Names (functions and constants)
        elif isinstance(node, ast.Name):
            if node.id in self.SAFE_FUNCTIONS:
                return self.SAFE_FUNCTIONS[node.id]()
            raise ValueError(f"Unknown identifier: {node.id}")

        # Mathematical operations
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.OPERATORS:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[type(node.op)](left, right)

        # Unary operations (like -5)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.OPERATORS:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            operand = self._eval_node(node.operand)
            return self.OPERATORS[type(node.op)](operand)

        # Function calls
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function call")
            if node.func.id not in self.SAFE_FUNCTIONS:
                raise ValueError(f"Unknown function: {node.func.id}")
                
            args = [self._eval_node(arg) for arg in node.args]
            return self.SAFE_FUNCTIONS[node.func.id](*args)

        # Everything else is not allowed
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    def _evaluate_expression(self, expression: str) -> Optional[int]:
        """Safely evaluate a mathematical expression."""
        try:
            # Try word to number first
            if len(expression.split()) == 1:
                try:
                    result = w2n.word_to_num(expression)
                    return result if len(str(abs(result))) <= self.max_digits else None
                except ValueError:
                    pass

            # Parse and evaluate mathematical expression
            tree = ast.parse(expression, mode='eval')
            result = self._eval_node(tree.body)
            
            # Enhanced validation for trigonometric and other float results
            if isinstance(result, (int, float)):
                # If result is a float, round it if it's very close to an integer
                if abs(result - round(result)) < 1e-10:
                    result_int = round(result)
                    if len(str(abs(result_int))) <= self.max_digits:
                        return result_int
                elif isinstance(result, int):
                    if len(str(abs(result))) <= self.max_digits:
                        return result
            return None
            
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, 
                OverflowError, MemoryError, RecursionError):
            return None

    def validate_count(self, expression: str, guild_id: str, user_id: str) -> Tuple[bool, bool, bool]:
        """
        Validate a count attempt and update statistics.
        Returns: (is_valid, is_prime, should_remove_role)
        """
        try:
            # Try to evaluate the expression
            number = self._evaluate_expression(expression)
            if number is None:
                return False, False, False
            
            with sqlite3.connect(self.db_path) as db:
                cursor = db.cursor()
                
                # Ensure server exists in database
                cursor.execute(
                    "INSERT OR IGNORE INTO server (serverID, count) VALUES (?, 1)",
                    (guild_id,)
                )
                
                # Ensure user exists in database
                cursor.execute(
                    "INSERT OR IGNORE INTO mathematicians (ID, serverID) VALUES (?, ?)",
                    (user_id, guild_id)
                )
                
                # Get current count and last counter
                cursor.execute(
                    "SELECT count, last_counter FROM server WHERE serverID = ?",
                    (guild_id,)
                )
                current_count, last_counter = cursor.fetchone()
                
                # Check if count is valid and user isn't counting twice
                if number != current_count or user_id == last_counter:
                    self._handle_failed_count(cursor, guild_id, user_id, current_count)
                    return False, False, False
                
                # Handle successful count
                is_prime = self.is_prime(number)
                self._handle_successful_count(cursor, guild_id, user_id, number, is_prime)
                
                db.commit()
                return True, is_prime, False
                
        except Exception as e:
            print(f"Error validating count: {e}")
            return False, False, False

    def _handle_failed_count(self, cursor: sqlite3.Cursor, guild_id: str, user_id: str, current_count: int) -> None:
        """Handle a failed count attempt."""
        # Update user stats
        cursor.execute("""
            UPDATE mathematicians 
            SET fails = fails + 1,
                last_fail = ?,
                last_fail_date = ?,
                delta_fail = 0
            WHERE ID = ? AND serverID = ?
        """, (current_count, time.time(), user_id, guild_id))
        
        # Update server stats
        cursor.execute("""
            UPDATE server 
            SET count = 1,
                fails = fails + 1,
                last_counter = ?
            WHERE serverID = ?
        """, (user_id, guild_id))


    def _handle_successful_count(self, cursor: sqlite3.Cursor, guild_id: str, user_id: str, 
                               number: int, is_prime: bool) -> None:
        """Handle a successful count."""
        # Update user stats
        cursor.execute("""
            UPDATE mathematicians 
            SET counts = counts + 1,
                high_score = MAX(high_score, ?),
                last_count = ?,
                primes = primes + ?
            WHERE ID = ? AND serverID = ?
        """, (number, number, 1 if is_prime else 0, user_id, guild_id))
        
        # Update server stats
        cursor.execute("""
            UPDATE server 
            SET count = ?,
                high_score = MAX(high_score, ?),
                counts = counts + 1,
                primes = primes + ?,
                last_counter = ?
            WHERE serverID = ?
        """, (number + 1, number, 1 if is_prime else 0, user_id, guild_id))

    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    def get_next_prime(self, guild_id: str) -> int:
        """Get the next prime number after current count."""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute("SELECT count FROM server WHERE serverID = ?", (guild_id,))
            current = cursor.fetchone()[0]
            
        number = current
        while not self.is_prime(number):
            number += 1
        return number

    def get_leaderboard(self, guild_id: str, category: str = 'counts', limit: int = 10) -> List[Tuple[int, str]]:
        """Get leaderboard for specified category."""
        valid_categories = {
            'counts': 'counts',
            'primes': 'primes',
            'fails': 'fails'
        }
        
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {list(valid_categories.keys())}")
            
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute(f"""
                SELECT {valid_categories[category]}, ID 
                FROM mathematicians 
                WHERE serverID = ? 
                ORDER BY {valid_categories[category]} DESC 
                LIMIT ?
            """, (guild_id, limit))
            return cursor.fetchall()

    def get_user_stats(self, guild_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a user."""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT last_count, counts, fails, high_score, 
                       last_fail, last_fail_date, primes 
                FROM mathematicians 
                WHERE serverID = ? AND ID = ?
            """, (guild_id, user_id))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return {
                'last_count': result[0],
                'total_counts': result[1],
                'total_fails': result[2],
                'highest_count': result[3],
                'last_fail_number': result[4],
                'last_fail_date': result[5],
                'prime_counts': result[6]
            }

    def get_user_last_count(self, guild_id: str) -> Optional[str]:
        """Get the user who made the last count."""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT last_counter FROM server WHERE serverID = ?", 
                (guild_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None