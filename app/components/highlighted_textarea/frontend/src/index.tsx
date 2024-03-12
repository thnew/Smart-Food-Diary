import { Streamlit, RenderData } from "streamlit-component-lib"

const container = document.querySelector(".textarea-container") as HTMLElement
const textarea = document.querySelector(".edit-content") as HTMLTextAreaElement

textarea.addEventListener("focus", () => container.classList.add("focused"))
textarea.addEventListener("blur", () => container.classList.remove("focused"))

let value: string = ""
textarea.addEventListener("blur", () => {
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

  console.log(value)
  console.log(inputValue)

  Streamlit.setComponentValue(textarea.innerText)
  Streamlit.setFrameHeight()
})

textarea.oninput = () => {
  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
}

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
    value = data.args["value"]
    textarea.innerText = value

    // We tell Streamlit to update our frameHeight after each render event, in
    // case it has changed. (This isn't strictly necessary for the example
    // because our height stays fixed, but this is a low-cost function, so
    // there's no harm in doing it redundantly.)
    Streamlit.setFrameHeight()

    let labels = await determineLabels(data)
    refreshLabels(labels)
  }
)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()

type LabelDefinition = [start: number, end: number, color: string]

async function determineLabels(data: RenderData) {
  showSpinner()
  await new Promise((resolve) => setTimeout(resolve, 3000))
  hideSpinner()

  return data.args["labels"] as [start: number, end: number, color: string][]
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
function refreshLabels(labels: LabelDefinition[]) {
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
