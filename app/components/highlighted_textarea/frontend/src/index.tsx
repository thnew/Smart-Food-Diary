import { Streamlit, RenderData } from "streamlit-component-lib"

const container = document.querySelector(".textarea-container") as HTMLElement
const textarea = document.querySelector(".edit-content") as HTMLTextAreaElement
const spinner = document.querySelector(".edit-content-spinner") as HTMLElement
const summary = document.querySelector(".summary") as HTMLElement

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

let apiUrl = ""
let initialized = false

let timeout: NodeJS.Timeout | undefined = undefined
textarea.addEventListener("keyup", async (e: any) => {
  if (!valueAndTextareaDiffer()) return

  if (textarea.value.trim() === "") {
    hideSummary()
    removeAllHighlightings()

    return new ExtractResults()
  }

  const affectedLabels = getSelectedLabelAndAllOnwards(textarea.selectionStart)
  if (affectedLabels) {
    affectedLabels.forEach((label) => {
      label.element.remove()
      displayedLabels.splice(displayedLabels.indexOf(label), 1)
    })
  }

  hideSummary()

  if (timeout) clearTimeout(timeout)
  timeout = setTimeout(async () => {
    Streamlit.setComponentValue({
      value: textarea.value,
      dataframe: await analyzeMeals(),
    })
  }, 500)
})

function getSelectedLabelAndAllOnwards(pointerIndex: number) {
  const selected = displayedLabels.find(
    (label) =>
      label.label.start <= pointerIndex && label.label.end >= pointerIndex
  )

  if (!selected) return undefined

  // Add all following labels
  const index = displayedLabels.indexOf(selected)

  console.log(displayedLabels.slice(index))
  return displayedLabels.slice(index)
}

textarea.addEventListener("keydown", async (e) => {
  if (!(e.metaKey || e.ctrlKey) || e.key !== "Enter") return

  Streamlit.setComponentValue({
    value: textarea.value,
    dataframe: await analyzeMeals(),
  })
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
    const value = data.args["initial_value"] || ""

    // We tell Streamlit to update our frameHeight after each render event, in
    // case it has changed. (This isn't strictly necessary for the example
    // because our height stays fixed, but this is a low-cost function, so
    // there's no harm in doing it redundantly.)
    Streamlit.setFrameHeight()

    if (!initialized) {
      console.log("INIT COMPONENT")
      textarea.value = value
      previousValue = value
      Streamlit.setComponentValue({
        value: value,
        dataframe: await analyzeMeals(),
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

type LabelDefinition = {
  start: number
  end: number
  color: string
  calories: number
}

const colors = [
  "#fbb4ae44",
  "#b3cee344",
  "#cceac444",
  "#decce444",
  "#fed9a544",
  "#ffffcb44",
  "#e6d8bd44",
  "#fddbec44",
  "#f2f2f244",
]

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

let previousValue = ""
function valueAndTextareaDiffer() {
  const current_value = previousValue
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")
  const input_value = textarea.value
    .split("\n")
    .map((x: string) => x.trim())
    .join("\n")

  const valueChanged = current_value !== input_value
  previousValue = textarea.value

  return valueChanged
}

let requestController: AbortController | undefined = undefined
async function analyzeMeals(): Promise<ExtractResults | undefined> {
  let text = textarea.value

  /* We replace all new lines with a space and a dot. Cause AI can't deal with
     them really well.
  */
  text = text.replaceAll("\n", " .")

  let resultParsed: ExtractResults
  try {
    showSpinner()
    hideSummary()

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
    showSummary()

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
}

function hideSpinner() {
  spinner.style.display = "none"
}

function showSummary() {
  summary.classList.remove("hidden")
}

function hideSummary() {
  summary.classList.add("hidden")
}

// Some functions
function refreshLabels(results: ExtractResults) {
  const labels = readLabelsFromResult(results)

  removeAllHighlightings()
  getLabeledText(textarea.value, labels).forEach((el) => container.prepend(el))
}

function removeAllHighlightings() {
  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
}

let displayedLabels: {
  element: HTMLDivElement
  label: LabelDefinition
}[] = []
function getLabeledText(text: string, labels: LabelDefinition[]): Node[] {
  const elements: Node[] = []

  displayedLabels = []
  labels.forEach((label) => {
    const labelContainer = document.createElement("div")
    labelContainer.classList.add("edit-content")
    labelContainer.classList.add("edit-content-back")

    displayedLabels.push({
      element: labelContainer,
      label: label,
    })

    // We add the original text before the label as plain text to keep the distance properly
    if (label.start > 0) {
      const preprendText = document.createElement("span")
      preprendText.classList.add("hightlight-prepend-text")
      preprendText.innerText = text.slice(0, label.start)
      labelContainer.appendChild(preprendText)
    }

    // Then we add the label
    const labelElement = document.createElement("div")
    labelElement.classList.add("highlight-text")

    const caloryLabel = document.createElement("div")
    caloryLabel.classList.add("highlight-text-label")
    caloryLabel.innerText = `${Math.round(label.calories)}cal`
    labelElement.appendChild(caloryLabel)

    if (label.color) labelElement.style.background = label.color

    labelElement.appendChild(
      document.createTextNode(text.slice(label.start, label.end))
    )
    labelContainer.appendChild(labelElement)

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
    labels.push({
      start,
      end,
      color,
      calories: resultParsed.matched_calories[i],
    })
  }

  return labels
}
