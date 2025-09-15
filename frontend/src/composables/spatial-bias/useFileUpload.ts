import type { Ref } from 'vue'
import Papa from 'papaparse'

export function useFileUpload(
  mode: Ref<'audit' | 'relabel' | 'threshold'>,
  indivInfoParsed: Ref<any[]>,
  indivInfoInput: Ref<string>,
  fitIndivParsed: Ref<any[]>,
  fitIndivInput: Ref<string>,
  predictIndivParsed: Ref<any[]>,
  predictIndivInput: Ref<string>,
  regionInfoParsed: Ref<any[]>,
  regionInfoInput: Ref<string>,
  predictRegionParsed: Ref<any[]>,
  predictRegionInput: Ref<string>
): {
  handleFileUpload: (event: Event, type: string) => void
} {
  function handleFileUpload(event: Event, type: string) {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = e => {
      const content = e.target?.result as string
      try {
        const isCSV = file.name.endsWith('.csv')
        const parsed = isCSV
          ? Papa.parse(content, { header: true, dynamicTyping: true }).data
          : JSON.parse(content)

        if (type === 'combined') {
          if (mode.value === 'audit' || mode.value === 'relabel') {
            indivInfoParsed.value = parsed.indiv ?? []
            regionInfoParsed.value = parsed.region ?? []

            indivInfoInput.value = JSON.stringify(parsed.indiv?.slice(0, 3), null, 2) + '\n...'
            regionInfoInput.value = JSON.stringify(parsed.region?.slice(0, 2), null, 2) + '\n...'
          }

          if (mode.value === 'threshold') {
            fitIndivParsed.value = parsed.fit_indiv ?? []
            predictIndivParsed.value = parsed.predict_indiv ?? []
            predictRegionParsed.value = parsed.predict_region ?? []

            fitIndivInput.value = JSON.stringify(parsed.fit_indiv?.slice(0, 3), null, 2) + '\n...'
            predictIndivInput.value = JSON.stringify(parsed.predict_indiv?.slice(0, 3), null, 2) + '\n...'
            predictRegionInput.value = JSON.stringify(parsed.predict_region?.slice(0, 2), null, 2) + '\n...'
          }
        } else {
          switch (type) {
            case 'indiv':
              indivInfoParsed.value = parsed
              indivInfoInput.value = JSON.stringify(parsed.slice(0, 3), null, 2) + '\n...'
              break
            case 'fit_indiv':
              fitIndivParsed.value = parsed
              fitIndivInput.value = JSON.stringify(parsed.slice(0, 3), null, 2) + '\n...'
              break
            case 'predict_indiv':
              predictIndivParsed.value = parsed
              predictIndivInput.value = JSON.stringify(parsed.slice(0, 3), null, 2) + '\n...'
              break
            case 'region':
              regionInfoParsed.value = parsed
              regionInfoInput.value = JSON.stringify(parsed.slice(0, 2), null, 2) + '\n...'
              break
            case 'predict_region':
              predictRegionParsed.value = parsed
              predictRegionInput.value = JSON.stringify(parsed.slice(0, 2), null, 2) + '\n...'
              break
          }
        }
      } catch (err) {
        alert('Error parsing file: ' + err)
      }
    }

    reader.readAsText(file)
  }

  return {
    handleFileUpload
  }
}
