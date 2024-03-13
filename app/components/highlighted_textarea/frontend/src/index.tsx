import { Streamlit, RenderData } from "streamlit-component-lib"

const container = document.querySelector(".textarea-container") as HTMLElement
const textarea = document.querySelector(".edit-content") as HTMLTextAreaElement

textarea.addEventListener("focus", () => container.classList.add("focused"))
textarea.addEventListener("blur", () => container.classList.remove("focused"))

let key = ""
let value = ""
textarea.addEventListener("blur", async () => {
  value = value
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")
  const inputValue = textarea.innerText
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")

  const valueChanged = value !== inputValue
  if (!valueChanged) return

  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
  const result = await analyzeMeals(textarea.innerText)

  console.log(value)
  console.log(inputValue)

  Streamlit.setComponentValue({
    value: inputValue,
    dataframe: result,
  })
  Streamlit.setFrameHeight()
})

textarea.addEventListener("input", () => {
  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
})

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
Streamlit.events.addEventListener(
  Streamlit.RENDER_EVENT,
  async (event: Event) => {
    // Get the RenderData from the event
    const data = (event as CustomEvent<RenderData>).detail

    console.log("Data received in the frontend: ", data)

    // RenderData.args is the JSON dictionary of arguments sent from the
    // Python script.
    key = data.args["key"]
    value = value || data.args["initial_value"] || ""
    textarea.innerText = value

    // We tell Streamlit to update our frameHeight after each render event, in
    // case it has changed. (This isn't strictly necessary for the example
    // because our height stays fixed, but this is a low-cost function, so
    // there's no harm in doing it redundantly.)
    Streamlit.setFrameHeight()

    await analyzeMeals(value)
  }
)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()

type LabelDefinition = [start: number, end: number, color: string]

const colors = ["#50C9CE", "#72A1E5", "#9883E5", "#FCD3DE"]

interface ExtractResults {
  food: string[]
  food_start: number[]
  food_end: number[]
  unit: string[]
  unit_start: number[]
  unit_end: number[]
  quantity: string[]
  quantity_start: number[]
  quantity_end: number[]
}

async function analyzeMeals(text: string): Promise<ExtractResults | undefined> {
  let resultParsed: ExtractResults
  try {
    showSpinner()
    await new Promise((resolve) => setTimeout(resolve, 1000))
    resultParsed = {
      food: ["Fanta"],
      food_start: [10],
      food_end: [15],
      unit: ["glasses"],
      unit_start: [2],
      unit_end: [9],
      quantity: ["2"],
      quantity_start: [0],
      quantity_end: [1],
    }

    // const result = await fetch(
    //   "https://ner-food-ctgsi4wqxa-ew.a.run.app?text=" + text
    // )

    // // TODO: Map to labels

    // console.log(result)

    refreshLabels(resultParsed)

    return resultParsed
  } catch (e) {
    console.error(e)
  } finally {
    console.log("OK")
    hideSpinner()
  }
}

function showSpinner() {
  const spinner = document.querySelector(".edit-content-spinner") as HTMLElement
  spinner.style.display = "block"
}

function hideSpinner() {
  const spinner = document.querySelector(".edit-content-spinner") as HTMLElement
  spinner.style.display = "none"
}

// Some functions
function refreshLabels(results: ExtractResults) {
  const labels = readLabelsFromResult(results)

  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
  getLabeledText(textarea.innerText, labels).forEach((el) =>
    container.prepend(el)
  )
}

function getLabeledText(text: string, labels: LabelDefinition[]): Node[] {
  const elements: Node[] = []

  labels.forEach(([start, end, color]) => {
    const labelContainer = document.createElement("div")
    labelContainer.classList.add("edit-content")
    labelContainer.classList.add("edit-content-back")

    // We add the original text before the label as plain text to keep the distance properly
    if (start > 0) {
      const preprendText = document.createElement("span")
      preprendText.classList.add("hightlight-prepend-text")
      preprendText.innerText = text.slice(0, start)
      labelContainer.appendChild(preprendText)
    }

    // Then we add the label
    const span = document.createElement("span")
    span.classList.add("highlight-text")
    if (color) span.style.background = color

    span.appendChild(document.createTextNode(text.slice(start, end)))
    labelContainer.appendChild(span)

    elements.push(labelContainer)
  })

  return elements
}

function readLabelsFromResult(resultParsed: any): LabelDefinition[] {
  const labels: LabelDefinition[] = []
  for (let i = 0; i < resultParsed.food.length; i++) {
    const start = Math.min(
      ...[
        resultParsed.food_start[i],
        resultParsed.quantity_start[i],
        resultParsed.unit_start[i],
      ].filter((x) => x >= 0)
    )
    const end = Math.max(
      ...[
        resultParsed.food_end[i],
        resultParsed.quantity_end[i],
        resultParsed.unit_end[i],
      ].filter((x) => x >= 0)
    )

    const color = colors[i % colors.length]
    labels.push([start, end, color])
  }

  return labels
}
