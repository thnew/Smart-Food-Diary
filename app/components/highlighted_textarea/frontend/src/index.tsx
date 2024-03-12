import { Streamlit, RenderData } from "streamlit-component-lib"

function getLabeledText(
  text: string,
  labels: [start: number, end: number, color: string][]
): Node[] {
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

// Add text and a button to the DOM. (You could also add these directly
// to index.html.)
const container = document.body.appendChild(document.createElement("div"))
container.classList.add("textarea-container")

const textarea = container.appendChild(document.createElement("div"))
textarea.classList.add("edit-content")
textarea.setAttribute("contenteditable", "true")

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, (event: Event) => {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail

  console.log("Data received in the frontend: ", data)

  textarea.onfocus = () => {
    container.classList.add("focused")
  }

  textarea.onblur = () => {
    container.classList.remove("focused")

    value = value
      .split("\n")
      .map((x: string) => x.trim())
      .join("\n")
    const inputValue = textarea.innerText
      .split("\n")
      .map((x: string) => x.trim())
      .join("\n")

    if (value === inputValue) return

    container
      .querySelectorAll(".edit-content-back")
      .forEach((el) => el.remove())

    console.log(value)
    console.log(inputValue)

    Streamlit.setComponentValue(textarea.innerText)
    Streamlit.setFrameHeight()
  }

  // RenderData.args is the JSON dictionary of arguments sent from the
  // Python script.
  let value = data.args["value"]
  let labels = data.args["labels"]

  // Show "Hello, name!" with a non-breaking space afterwards.
  textarea.oninput = () => {
    container
      .querySelectorAll(".edit-content-back")
      //.forEach((el) => el.remove())
      .forEach((el) => ((el as HTMLElement).style.opacity = "0"))
  }
  textarea.innerText = value

  container.querySelectorAll(".edit-content-back").forEach((el) => el.remove())
  getLabeledText(textarea.innerText, labels).forEach((el) =>
    container.prepend(el)
  )

  // We tell Streamlit to update our frameHeight after each render event, in
  // case it has changed. (This isn't strictly necessary for the example
  // because our height stays fixed, but this is a low-cost function, so
  // there's no harm in doing it redundantly.)
  Streamlit.setFrameHeight()
})

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()
