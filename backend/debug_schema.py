from pydantic import BaseModel, TypeAdapter
import app.schemas as s

print(s.OrderOut, s.__file__)
print(issubclass(s.OrderOut, BaseModel))
TypeAdapter(s.OrderOut)
print("OK, OrderOut hợp lệ")