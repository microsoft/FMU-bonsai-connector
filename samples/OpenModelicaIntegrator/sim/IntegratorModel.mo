model Integrator "A simple integrator that, in each step, adds u to x."
  input Real u(start = 2.0, fixed = false);
  output Real x(start = 10.0, fixed = false);
equation
  der(x) = u;
end Integrator;
