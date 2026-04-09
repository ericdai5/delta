# Delta — Video Script (~3 min)

## INTRO (0:00 – 0:20)

Delta lowers the barrier and raises the ceiling for interactive formula explanations. Authors use declarative constructs, while Delta handles substitution, synchronization, and walkthrough sequencing. This video shows the authoring process and highlights several examples.

---

## PART 1: Kinetic Energy — Building Up (0:15 – 1:15)

To see how Delta helps authors, let's walk through building an interactive kinetic energy formula.

### Formulas and Variables

To display the kinetic energy formula with labelled variables, we write a **formula entry** — just a LaTeX string with an id — and **variable entries**, naming each one by its LaTeX symbol and configuring simple properties like a display name. Delta renders the formula and recognizes each variable, highlighting it on hover.

```js
formulas: [{
  id: "kinetic-energy",
  latex: "K = \\frac{1}{2} m v^2",
}],
variables: {
  K: { name: "Kinetic energy" },
  m: { name: "Mass" },
  v: { name: "Velocity" },
},
```

### Defaults and Semantics

Right now the formula just shows symbols. To get a concrete calculation, we add a **default** to each variable entry and write a **semantics function** — plain JavaScript that computes K from m and v through a `vars` object Delta provides. Delta substitutes the defaults in and displays the computed result.

```js
formulas: [{
  id: "kinetic-energy",
  latex: "K = \\frac{1}{2} m v^2",
}],
variables: {
  K: { name: "Kinetic energy" },
  m: { default: 1, name: "Mass" },
  v: { default: 2, name: "Velocity" },
},
semantics: function ({ vars }) {
  vars.K = 0.5 * vars.m * Math.pow(vars.v, 2);
},
```

### Inline Input

With Delta, variables can be easily made interactive. Setting the input type to inline on mass turns it into an editable field right on the formula — type a new value and K recomputes instantly.

```js
m: {
  default: 1,
  range: [0, 10],
  input: "inline",
  name: "Mass",
  latexDisplay: "value",
  labelDisplay: "name",
},
```

### Drag Input

Setting the input type to drag with a range on velocity makes it draggable — click and drag directly on the rendered symbol to sweep through values and watch K update continuously.

```js
v: {
  default: 2,
  range: [0, 10],
  input: "drag",
  name: "Velocity",
},
```

### Graph

To visualize how K changes with v, we add a sample() call provided by Delta inside the semantics function to collect coordinates for graphing. Then we add a connection, here a graph2d configuration, where we define Delta line and point objects that use the collected sample data to plot the curve. We can also declare an interaction and the variable it controls.

The result is a bidirectionally linked graph and formula visualization where dragging on the graph changes the variable and the formula updates in sync. This interactive experience combines a labeled formula, live computation, two kinds of input, and a linked graph, all from a short declarative spec. Rather than writing custom code for each piece, we configure a few well-defined constructs that handle the common cases out of the box, with room for more elaborate augmentations when needed.

```js
semantics: function ({ vars, sample }) {
  vars.K = 0.5 * vars.m * Math.pow(vars.v, 2);
  sample("energy", { x: vars.v, y: vars.K });
},
graph2d: [{
  id: "energyGraph",
  xAxisVar: "v",
  yAxisVar: "K",
  lines: [{
    sampleId: "energy", parameter: "v",
    interaction: ["vertical-drag", "m"],
  }],
  points: [{
    sampleId: "energy",
    interaction: ["horizontal-drag", "v"],
  }],
}],
```

---

## PART 2: Average — Stepping (1:15 – 1:45)

### Formulas and Variables

For a new example, here's the mean formula. The spec starts the same way: a formula entry and variable entries.

```js
const config = {
  formulas: [
    {
      id: "average",
      latex: "\\mu = \\frac{1}{n} \\sum_{i=1}^{n} X_i"
    },
  ],
  variables: {
    "\\mu": { name: "Mean" },
    n: { name: "Count" },
    X_i: { name: "Value at index i", precision: 0 },
    X: { default: [10, 20, 30], name: "Value set" },
  },
};
```

### Semantics

Adding a semantics function loops through the dataset, accumulating the sum and computing the running average.

```js
semantics: function({ vars }) {
  vars.n = vars.X.length;
  var sum = 0;
  vars["\\mu"] = 0;
  for (var i = 0; i < vars.n; i++) {
    vars.X_i = vars.X[i];
    sum = sum + vars.X_i;
    vars["\\mu"] = sum / (i + 1);
  }
  vars["\\mu"] = Math.round(vars["\\mu"] * 100) / 100;
},
```

### Stepping

Some formulas are better understood one iteration at a time. Enabling `stepping: true` and calling `step()` inside the loop turns the computation into a clickable walkthrough. Each iteration snapshots its values onto the formula, and the reader can step forward and back to see how the average converges.

```js
stepping: true,
semantics: function({ vars, step }) {
  ...
    step({
      description: "Running average at index " + i + " is " + vars["\\mu"],
    });
  ...
},
```

### Step Labels

Each step can also attach labels to specific expressions in the formula, showing intermediate values right where they appear in the math.

```js
step({
  description: "Running average at index " + i + " is " + vars["\\mu"],
  labels: {
    "\\sum_{i=1}^{n} X_i": "sum is now " + sum,
    "n": "n is now " + (i + 1),
    "X_i": vars.X_i,
    "X": vars.X,
  },
});
```

---

## PART 3: Gradient Descent — Everything Together (1:45 – 2:30)

Many Delta specs will be as simple as the ones we've just seen — a formula, a few variables, and a semantics function. To show what's possible in more complex cases, here's a full gradient descent visualization using the same constructs.

The reader can step through six iterations of gradient descent, watching the loss, error, and gradient update on each step. A linked graph tracks the weight and loss over time, drawing the loss curve. Points mark the weight at each step, appearing progressively as the reader steps through. Vectors draw curved arrows from each step's starting position to its ending position, showing the direction and magnitude of each weight update. And everything is interactive — drag the learning rate or starting weight on the formula, or drag directly on the graph, and it all stays in sync.

### Familiar Parts

The full config behind it is 65 lines. The skeleton is the same as before. Two formula entries define the loss function and the weight update rule. Six variable entries name each symbol with defaults. The semantics function loops through iterations, computing the error, loss, and gradient. Inside the semantics loop, `sample()` collects coordinates for the graph, and `step()` snapshots each iteration's values onto both formulas.

```js
formulas: [
  { id: "loss-function", latex: "L = (y - w_t \\cdot x)^2" },
  { id: "update-weight", latex: "w_{t+1} = w_t - \\alpha \\cdot (-2x(y - w_t \\cdot x))" },
],
variables: {
  L:           { name: "Loss" },
  w_t:         { default: 0.5, name: "Current Weight" },
  "w_{t+1}":   { default: 0.5, name: "Next Weight" },
  "\\alpha":   { default: 0.1, input: "drag", range: [0, 1], name: "Learning Rate" },
  x:           { default: 1.5, input: "drag", range: [0, 4], name: "Feature" },
  y:           { default: 3.0, input: "drag", range: [0, 4], name: "Label" },
},
```

### What's New: Stepping and Sampling

```js
stepping: true,
semantics: function ({ vars, sample, step, latex }) {
  var w = vars.w_t;
  for (var t = 0; t < 6; t++) {
    var error = vars.y - w * vars.x;
    var loss = error * error;
    var gradient = -2 * vars.x * error;
    sample("initial-loss", { x: w, y: loss });
    step({
      "loss-function": {
        labels: {
          "L": "Loss is " + latex(loss).precision(2),
          "y - w_t \\cdot x": "Error is " + latex(error).precision(2),
        },
      },
      "update-weight": {
        labels: {
          "w_t": w, "\\alpha": vars["\\alpha"],
          "w_{t+1}": w - vars["\\alpha"] * gradient,
          "(-2x(y - w_t \\cdot x)": "Gradient is " + latex(gradient).precision(2),
        },
      },
    }, "gd-step");
    w -= vars["\\alpha"] * gradient;
    vars.L = (vars.y - w * vars.x) * (vars.y - w * vars.x);
    sample("final-loss", { x: w, y: vars.L });
  }
  vars["w_{t+1}"] = w;
},
```

### What's New: The Graph

The `graph2d` block wires the visualization to work with stepping. **Points** and **vectors** both reference the step ID defined earlier in the semantics — this single link is what synchronizes them with the walkthrough. Turning persistence setting to true makes step-connected points or vectors accumulate on the graph as the reader advances.

```js
graph2d: [{
  id: "gradient-descent",
  xAxisVar: "w_t", yAxisVar: "L",
  yRange: [-5, 10], xRange: [0, 4],
  lines: [{
    sampleId: "initial-loss",
    parameter: "w_t",
    interaction: ["horizontal-drag", "y"],
  }],
  points: [{
    sampleId: "initial-loss",
    stepId: "gd-step", persistence: true,
  }],
  vectors: [{
    startSampleId: "initial-loss", endSampleId: "final-loss",
    stepId: "gd-step", persistence: true,
    curved: -1,
  }],
}],
```

---

## PART 4: Example Reel (2:30 – 3:00)

Here are a few more examples.

In this vector addition example, scrubbing scalar coefficients updates the resulting vector calculation and the corresponding graph.

In this probability operations example, scrubbing the shared variable for intersection probability in one equation simultaneously updates the other.

In this matrix multiplication example, Custom external controls such as buttons can reconfigure the entire matrix while individual variables can still be interacted with.

This example showcases when an author substitute dynamic SVGs directly into an exponential decay formula. Here, radiation signs glow and clocks tick faster as values change.

This harmonic motion example also uses dynamic graphical labels to hint at what each parameter controls.
