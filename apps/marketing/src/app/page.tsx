import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">🧮 Beregne 2.0</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Link href="#features" className="text-gray-600 hover:text-gray-900">
                Funksjoner
              </Link>
              <Link href="#partners" className="text-gray-600 hover:text-gray-900">
                Partnere
              </Link>
              <Link href="#demo" className="text-gray-600 hover:text-gray-900">
                Demo
              </Link>
              <Link href="http://127.0.0.1:8000/dashboard" target="_blank">
                <Button variant="outline">Dashboard</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative px-4 pt-16 pb-20 sm:px-6 lg:pt-24 lg:pb-28 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
              <span className="block">AI-drevet</span>
              <span className="block text-blue-600">kalkulatorplattform</span>
              <span className="block">for Norge</span>
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Embed intelligente AI-agenter på din nettside. Fra oppussingsberegninger til lånekalkulator - 
              alt tilpasset dine kunder og ditt brand.
            </p>
            <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
              <div className="rounded-md shadow">
                <Link href="http://127.0.0.1:8000/dashboard" target="_blank">
                  <Button size="lg" className="w-full">
                    🚀 Kom i gang gratis
                  </Button>
                </Link>
              </div>
              <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                <Button variant="outline" size="lg" className="w-full">
                  Se demo
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Kraftige AI-agenter for din bedrift
            </h2>
            <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
              Spesialiserte beregningsagenter som forstår norske regler og kundens behov
            </p>
          </div>

          <div className="mt-16">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-red-100 rounded-lg">
                      🏠
                    </div>
                    <div>
                      <CardTitle>Oppussingsrådgiver</CardTitle>
                      <Badge variant="secondary">househacker</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Beregner materialer, kostnader og mengder for oppussingsprosjekter. 
                    Støtter maling, fliser, laminat og komplette romrenoveringer.
                  </CardDescription>
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      ✅ Materialkalkulator
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      ✅ Kostnadsestimater
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      ✅ Norske priser
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-green-100 rounded-lg">
                      🏦
                    </div>
                    <div>
                      <CardTitle>Lånekalkulator</CardTitle>
                      <Badge variant="outline">Kommer snart</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Boliglån, billån og forbrukslån med norske regler. 
                    Inkluderer 5x-regel, 85% belåningsgrad og effektiv rente.
                  </CardDescription>
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Norske låneregelverk
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Månedlige betalinger
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Maksimalt lånebeløp
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      ⚡
                    </div>
                    <div>
                      <CardTitle>Energirådgiver</CardTitle>
                      <Badge variant="outline">Kommer snart</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Sanntids strømpriser, energisparing og varmepumpekalkulator. 
                    Integrert med hvakosterstrommen.no.
                  </CardDescription>
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Sanntids strømpriser
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Energispareberegninger
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      🔄 Varmepumpe vs elektrisk
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Se househacker-agenten i aksjon
            </h2>
            <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
              Live demo av oppussingsrådgiveren med househacker sitt design
            </p>
          </div>

          <div className="mt-16 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <h3 className="text-lg font-medium text-gray-900">
                  househacker Oppussingsrådgiver
                </h3>
                <p className="text-sm text-gray-600">
                  Embedded widget - slik den vises på househacker.no
                </p>
              </div>
              <div className="p-6">
                <iframe 
                  src="http://127.0.0.1:8000/widget/househacker"
                  width="100%"
                  height="600"
                  className="border-0 rounded-lg"
                  title="househacker Widget Demo"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Partners Section */}
      <section id="partners" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              For entreprenører og bedrifter
            </h2>
            <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
              Embed intelligente kalkulatorer på din nettside og øk kundeengasjement
            </p>
          </div>

          <div className="mt-16">
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">🎯 For partnere</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium">Konfigurerbart design</h4>
                      <p className="text-gray-600">Tilpass farger, logo og meldinger til ditt brand</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium">Enkelt å implementere</h4>
                      <p className="text-gray-600">Legg til med én linje kode - iframe eller JavaScript</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium">Økt kundeengasjement</h4>
                      <p className="text-gray-600">Gi kundene umiddelbar verdi og kvalifiserte leads</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">🚀 Kom i gang</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">1</Badge>
                      <span>Opprett partner-profil i dashboardet</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">2</Badge>
                      <span>Konfigurer design og agenter</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">3</Badge>
                      <span>Kopier embed-kode til din nettside</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">4</Badge>
                      <span>Følg statistikk og forbedre</span>
                    </div>
                  </div>
                  
                  <div className="pt-4">
                    <Link href="http://127.0.0.1:8000/dashboard" target="_blank">
                      <Button className="w-full">
                        Åpne Partner Dashboard
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            Klar til å øke konvertering på nettsiden din?
          </h2>
          <p className="mt-4 text-xl text-blue-100">
            Gi kundene dine intelligente kalkulatorer som leverer umiddelbar verdi
          </p>
          <div className="mt-8">
            <Link href="http://127.0.0.1:8000/dashboard" target="_blank">
              <Button size="lg" variant="secondary" className="mr-4">
                Start gratis
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-blue-600">
              Book demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <Link href="#" className="text-gray-400 hover:text-gray-300">
              Vilkår
            </Link>
            <Link href="#" className="text-gray-400 hover:text-gray-300">
              Personvern
            </Link>
            <Link href="mailto:support@beregne.no" className="text-gray-400 hover:text-gray-300">
              Kontakt
            </Link>
          </div>
          <div className="mt-8 md:mt-0 md:order-1">
            <p className="text-center text-base text-gray-400">
              &copy; 2024 Beregne 2.0. Laget med ❤️ i Norge 🇳🇴
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}