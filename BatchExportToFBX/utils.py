def validate_prefix(self, context):
    if self.prefix and not self.prefix.endswith('_'):
        self.prefix += '_'
        print(f"Added missing underscore to prefix: {self.prefix}")