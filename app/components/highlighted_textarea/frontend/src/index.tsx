import { Streamlit, RenderData } from "streamlit-component-lib"

const container = document.querySelector(".textarea-container") as HTMLElement
const textarea = document.querySelector(".edit-content") as HTMLTextAreaElement
const spinner = document.querySelector(".edit-content-spinner") as HTMLElement

const summary = document.querySelector(".summary-overlay") as HTMLElement
const summaryButton = document.querySelector(".summary-button") as HTMLElement
summaryButton.onclick = () => summary.classList.remove("summary-overlay-hidden")
const closeSummaryButton = document.querySelector(".close-summary-button") as HTMLElement
closeSummaryButton.onclick = () => summary.classList.add("summary-overlay-hidden")

const totalCalories = document.querySelectorAll(
  ".total-calories"
) as NodeListOf<HTMLElement>
const totalFats = document.querySelectorAll(
  ".total-fats"
) as NodeListOf<HTMLElement>
const totalCarbs = document.querySelectorAll(
  ".total-carbs"
) as NodeListOf<HTMLElement>
const totalProteins = document.querySelectorAll(
  ".total-proteins"
) as NodeListOf<HTMLElement>

textarea.addEventListener("focus", () => container.classList.add("focused"))
textarea.addEventListener("blur", () => container.classList.remove("focused"))

let key = ""
let value = ""
let apiUrl = ""
let initialized = false

textarea.addEventListener("blur", async () => {
  if (!valueAndTextareaDiffer()) return

  value = textarea.innerText
  Streamlit.setFrameHeight()

  console.log("Value changed")

  Streamlit.setComponentValue({
    value: textarea.innerText,
    dataframe: await analyzeMeals(textarea.innerText),
  })
})

textarea.addEventListener("keydown", async (e) => {
  if (!(e.metaKey || e.ctrlKey) || e.key !== "Enter") return

  value = textarea.innerText
  Streamlit.setComponentValue({
    value: value,
    dataframe: await analyzeMeals(value),
  })
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

    // RenderData.args is the JSON dictionary of arguments sent from the
    // Python script.
    apiUrl = data.args["api_url"]
    key = data.args["key"]
    value = value || data.args["initial_value"] || ""
    textarea.innerText = value

    // We tell Streamlit to update our frameHeight after each render event, in
    // case it has changed. (This isn't strictly necessary for the example
    // because our height stays fixed, but this is a low-cost function, so
    // there's no harm in doing it redundantly.)
    Streamlit.setFrameHeight()

    if (!initialized) {
      Streamlit.setComponentValue({
        value: value,
        dataframe: await analyzeMeals(value),
      })

      initialized = true
    }
  }
)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()

type LabelDefinition = [
  start: number,
  end: number,
  color: string,
  calories: number
]

const colors = ["#50C9CE", "#72A1E5", "#9883E5", "#FCD3DE"]

class ExtractResults {
  name: string[] = []
  name_start: number[] = []
  name_end: number[] = []
  unit: string[] = []
  unit_start: number[] = []
  unit_end: number[] = []
  amount: string[] = []
  amount_start: number[] = []
  amount_end: number[] = []
  matched_name: string[] = []
  matched_amount: string[] = []
  matched_unit: string[] = []
  matched_calories: number[] = []
  matched_carbs: number[] = []
  matched_protein: number[] = []
  matched_fat: number[] = []
}

function valueAndTextareaDiffer() {
  const current_value = value
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")
  const input_value = textarea.innerText
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")

  const valueChanged = current_value !== input_value
  return valueChanged
}

let requestController: AbortController | undefined = undefined
async function analyzeMeals(text: string): Promise<ExtractResults | undefined> {
  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())

  if (text.trim() === "") return new ExtractResults()

  let resultParsed: ExtractResults
  try {
    showSpinner()
    // await new Promise((resolve) => setTimeout(resolve, 1000))
    // resultParsed = {
    //   name: ["Fanta", "Steak"],
    //   name_start: [10, 22],
    //   name_end: [15, 27],
    //   unit: ["glasses", ""],
    //   unit_start: [2, -1],
    //   unit_end: [9, -1],
    //   amount: ["2", "a"],
    //   amount_start: [0, 20],
    //   amount_end: [1, 21],
    //   matched_name: ["Subway Fanta", "Blockhouse Steak"],
    //   matched_amount: ["2", "a"],
    //   matched_unit: ["glasses", ""],
    //   matched_calories: [200, 300],
    //   matched_carbs: [20, 30],
    //   matched_protein: [10, 15],
    //   matched_fat: [5, 10],
    // }

    if (requestController) {
      requestController.abort()
    }

    requestController = new AbortController()
    const result = await fetch(apiUrl + "?text=" + text, {
      signal: requestController.signal,
    })

    resultParsed = (await result.json()) as ExtractResults

    refreshLabels(resultParsed)

    totalCalories.forEach(
      (el) =>
        (el.innerText = Math.round(
          resultParsed.matched_calories.reduce((p, total) => p + total, 0)
        ).toString())
    )
    totalFats.forEach(
      (el) =>
        (el.innerText = Math.round(
          resultParsed.matched_fat.reduce((p, total) => p + total, 0)
        ).toString())
    )
    totalCarbs.forEach(
      (el) =>
        (el.innerText = Math.round(
          resultParsed.matched_carbs.reduce((p, total) => p + total, 0)
        ).toString())
    )
    totalProteins.forEach(
      (el) =>
        (el.innerText = Math.round(
          resultParsed.matched_protein.reduce((p, total) => p + total, 0)
        ).toString())
    )
    hideSpinner()

    return resultParsed
  } catch (e) {
    const abort = (e as DOMException).name === "AbortError"

    console.error(e)

    if (!abort) hideSpinner()
    return new ExtractResults()
  }
}

function showSpinner() {
  spinner.style.display = "block"
  totalCalories.forEach((el) => (el.style.display = "none"))
}

function hideSpinner() {
  spinner.style.display = "none"
  totalCalories.forEach((el) => (el.style.display = "block"))
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

  labels.forEach(([start, end, color, calories]) => {
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
    const label = document.createElement("div")
    label.classList.add("highlight-text")

    const caloryLabel = document.createElement("div")
    caloryLabel.classList.add("highlight-text-label")
    caloryLabel.innerText = `${Math.round(calories)}ccal`
    label.appendChild(caloryLabel)

    if (color) label.style.background = color

    label.appendChild(document.createTextNode(text.slice(start, end)))
    labelContainer.appendChild(label)

    elements.push(labelContainer)
  })

  return elements
}

function readLabelsFromResult(resultParsed: ExtractResults): LabelDefinition[] {
  const labels: LabelDefinition[] = []
  for (let i = 0; i < resultParsed.name.length; i++) {
    const start = Math.min(
      ...[
        resultParsed.name_start[i],
        resultParsed.amount_start[i],
        resultParsed.unit_start[i],
      ].filter((x) => x >= 0)
    )
    const end = Math.max(
      ...[
        resultParsed.name_end[i],
        resultParsed.amount_end[i],
        resultParsed.unit_end[i],
      ].filter((x) => x >= 0)
    )

    const color = colors[i % colors.length]
    labels.push([start, end, color, resultParsed.matched_calories[i]])
  }

  return labels
}
